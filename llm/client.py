import os
import time
import requests
from dotenv import load_dotenv  # type: ignore

load_dotenv()

REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "60"))
MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
RETRY_BACKOFF_SECONDS = float(os.getenv("LLM_RETRY_BACKOFF_SECONDS", "2"))


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def post_with_retries(url, *, headers, json, timeout):
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=json,
                timeout=timeout,
            )

            if response.status_code in (429, 500, 502, 503, 504):
                last_error = f"HTTP {response.status_code}: {response.text[:500]}"

                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue

            response.raise_for_status()
            return response

        except (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
        ) as e:
            last_error = str(e)

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue

            raise

        except requests.exceptions.RequestException:
            raise

    raise requests.exceptions.RequestException(
        f"Request failed after {MAX_RETRIES} attempts: {last_error}"
    )


def call_llm(messages):
    provider = get_env("LLM_PROVIDER", "ollama")
    provider = provider.lower() if provider else "ollama"

    if provider == "ollama":
        return call_ollama(messages)
    if provider == "openai":
        return call_openai(messages)

    return f"ERROR: Unsupported LLM_PROVIDER '{provider}'"


def call_ollama(messages):
    base_url = get_env("OLLAMA_BASE_URL", "http://localhost:11434")
    model = get_env("OLLAMA_MODEL", "llama3")
    api_key = get_env("OLLAMA_API_KEY")

    if not base_url:
        return "ERROR: OLLAMA_BASE_URL not set"

    if not model:
        return "ERROR: OLLAMA_MODEL not set"

    url = f"{base_url.rstrip('/')}/api/chat"

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
    }

    headers = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = post_with_retries(
            url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        data = response.json()
        content = data.get("message", {}).get("content")

        if not content:
            return f"ERROR: Ollama response missing message content: {data}"

        return content

    except requests.exceptions.Timeout:
        return "ERROR: Ollama request timed out after retries"
    except requests.exceptions.RequestException as e:
        return f"ERROR: Ollama request failed after retries → {str(e)}"
    except ValueError as e:
        return f"ERROR: Failed to parse Ollama JSON response → {str(e)}"
    except Exception as e:
        return f"ERROR: Unexpected Ollama error → {str(e)}"


def call_openai(messages):
    api_key = get_env("OPENAI_API_KEY")
    model = get_env("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return "ERROR: OPENAI_API_KEY not set"

    if not model:
        return "ERROR: OPENAI_MODEL not set"

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }

    try:
        response = post_with_retries(
            url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        data = response.json()
        choices = data.get("choices", [])

        if not choices:
            return f"ERROR: OpenAI response missing choices: {data}"

        content = choices[0].get("message", {}).get("content")

        if not content:
            return f"ERROR: OpenAI response missing message content: {data}"

        return content

    except requests.exceptions.Timeout:
        return "ERROR: OpenAI request timed out after retries"
    except requests.exceptions.RequestException as e:
        return f"ERROR: OpenAI request failed after retries → {str(e)}"
    except ValueError as e:
        return f"ERROR: Failed to parse OpenAI JSON response → {str(e)}"
    except Exception as e:
        return f"ERROR: Unexpected OpenAI error → {str(e)}"
