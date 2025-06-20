import { ErrorDto } from "../dto/misc/ErrorDto";
import { API_URL, isDevelopment } from "../env";

export const DEFAULT_HEADERS: Record<string, string> = {
    "Content-Type": "application/json",
};

interface FetchParams {
    method: string;
    headers?: Record<string, string>;
    credentials?: RequestCredentials;
    body?: string | FormData;
}

/**
 * Custom wrapper around the native fetch function to return a proper error response
 * that fits this app's conventions
 * @param url the api path (excluding the base url) should always start with a "/"
 * @param params 
 * @returns 
 */
export function callFetch(
    url: string,
    params: FetchParams,
): Promise<Response | ErrorDto> {
    const unexpectedErrorMessage = "An unexpected error occured.";

    return new Promise((resolve, reject) => {
        fetch(`${API_URL}${url}`, {
            method: params.method,
            headers: params.headers,
            credentials: params.credentials,
            body: params.body,
        })
            .then(async (response) => {
                if (response.ok) {
                    resolve(response);
                    // The server returned an error
                } else {
                    // The server's errors should always return a JSON in the form of {error: <error message>}
                    const responseJson: ErrorDto = await response.json();
                    const responseStatus = response.status;
                    const errorMessage = responseJson.error || response.statusText;

                    if (isDevelopment && responseStatus === 500) {
                        console.error(errorMessage);
                    }

                    // Create the error dto object to propagate
                    reject({
                        error:
                            responseStatus === 500
                                ? unexpectedErrorMessage
                                : errorMessage,
                        displayToUser: responseJson.displayToUser,
                        socketConnectionKiller: responseJson.socketConnectionKiller
                    } as ErrorDto);
                }
            })
            // fetching error, when the server is down mostly
            .catch(() => {
                if (isDevelopment) {
                    reject({
                        error: `Failed to fetch the URL ${API_URL}${url}`,
                        // Other fields are false by default
                    } as ErrorDto);
                }
                reject({
                    error: unexpectedErrorMessage,
                } as ErrorDto);
            });
    });
}

/**
 * @param url the api path (excluding the base url) should always start with a "/"
 * @param params 
 * @returns The fetched data's json parsed into the given type
 * @throws 
 */
export function fetchAs<T>(
    url: string,
    params: FetchParams,
): Promise<T> {
    return new Promise((resolve, reject) => {
        callFetch(url, params)
            .then(async (response) => {
                if ('json' in response) {
                    // response is of type Response
                    const data = await response.json();
                    resolve(data as T);
                } else {
                    // response is of type ErrorDto, in which case you propagate it
                    reject(response);
                }
            })
            // propagate the error
            .catch((error: ErrorDto) => {
                reject(error);
            });
    });
}