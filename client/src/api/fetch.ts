import { isDevelopment } from "../env";

export const API_URL = process.env.REACT_APP_API_URL;

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

export function callFetch<T>(
    url: string,
    params: FetchParams,
): Promise<T> {
    const unexpectedError = "An unexpected error occured.";

    return new Promise<T>((resolve, reject) => {
        fetch(`${API_URL}${url}`, {
            method: params.method,
            headers: params.headers,
            credentials: params.credentials,
            body: params.body,
        })
            .then(async (response) => {
                if (response.ok) {
                    resolve(response.json() as T);
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
                                ? unexpectedError
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
                    message: unexpectedError,
                } as ErrorResponse);
            });
    });
}