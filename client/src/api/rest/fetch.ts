import { API_URL, isDevelopment } from "../../env";

export const DEFAULT_HEADERS: Record<string, string> = {
    "Content-Type": "application/json",
};

interface FetchParams {
    method: string;
    headers?: Record<string, string>;
    credentials?: RequestCredentials;
    body?: string | FormData;
}

export interface ErrorResponse {
    code: number;
    message: string;
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
): Promise<Response | ErrorResponse> {
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
                } else {
                    // The server's errors should always return a JSON in the form of {error: <error message>}
                    const responseJson: { error: string } = await response.json();
                    const responseStatus = response.status;
                    const errorMessage = responseJson.error || response.statusText;

                    if (isDevelopment && responseStatus === 500) {
                        console.error(errorMessage);
                    }

                    reject({
                        code: responseStatus,
                        message:
                            responseStatus === 500
                                ? unexpectedErrorMessage
                                : errorMessage,
                    } as ErrorResponse);
                }
            })
            .catch(() => {
                if (isDevelopment) {
                    reject({
                        code: 500,
                        message: `Failed to fetch the URL ${API_URL}${url}`,
                    } as ErrorResponse);
                }
                reject({
                    code: 500,
                    message: unexpectedErrorMessage,
                } as ErrorResponse);
            });
    });
}

/**
 * 
 * @param url the api path (excluding the base url) should always start with a "/"
 * @param params 
 * @returns 
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
                    // response is of type ErrorResponse
                    reject(response);
                }
            })
            .catch((error: ErrorResponse) => {
                reject(error);
            });
    });
}