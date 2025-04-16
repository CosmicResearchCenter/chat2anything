// http.ts

// 添加token相关的工具函数
export const saveToken = (token: string) => {
    localStorage.setItem('token', token);
};

export const getToken = () => {
    return localStorage.getItem('token');
};

export const removeToken = () => {
    localStorage.removeItem('token');
};

// 新增：获取认证请求头
const getAuthHeaders = (customHeaders?: any) => {
    const token = getToken();
    const defaultHeaders = {
        'Authorization': token ? `Bearer ${token}` : '',
        // 'Content-Type': 'application/json'
    };
    return customHeaders ? { ...defaultHeaders, ...customHeaders } : defaultHeaders;
};

export async function getRequest<T>(url: string): Promise<T | undefined> {
    try {
        const headers = getAuthHeaders();
        const response = await fetch(url, {
            method: 'GET',
            headers
        });

        if (!response.ok) {
            if (response.status === 401) {
                removeToken(); // token无效时清除
            }
            throw new Error(`GET request failed: ${response.statusText}`);
        }

        return await response.json() as T; // assuming the response is JSON
    } catch (error) {
        console.error('GET request error:', error);
        return undefined;
    }
}

export async function postRequest<T>(url: string, body: any, customHeaders?: any): Promise<T | undefined> {
    try {
        const isFormData = body instanceof FormData;
        const headers = isFormData 
            ? { ...getAuthHeaders(customHeaders) }
            : {...getAuthHeaders(customHeaders),'Content-Type': 'application/json'};

        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: isFormData ? body : JSON.stringify(body),
        });

        if (!response.ok) {
            if (response.status === 401) {
                removeToken();
            }
            throw new Error(`POST request failed: ${response.statusText}`);
        }

        return await response.json() as T;
    } catch (error) {
        console.error('POST request error:', error);
        return undefined;
    }
}

export async function putRequest<T>(url: string, body: any, customHeaders?: any): Promise<T | undefined> {
    try {
        const isFormData = body instanceof FormData;
        const headers = isFormData 
            ? { ...getAuthHeaders(customHeaders) }
            : {...getAuthHeaders(customHeaders),'Content-Type': 'application/json'};
        const response = await fetch(url, {
            method: 'PUT',
            headers,
            body: isFormData ? body : JSON.stringify(body),
        });

        if (!response.ok) {
            if (response.status === 401) {
                removeToken();
            }
            throw new Error(`PUT request failed: ${response.statusText}`);
        }

        // 确保响应体为 JSON 格式再解析
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return await response.json() as T;
        }

        // 如果不是 JSON 格式，返回空
        return undefined;
    } catch (error) {
        console.error('PUT request error:', error);
        return undefined;
    }
}

export async function deleteRequest<T>(url: string): Promise<T | undefined> {
    try {
        const headers = getAuthHeaders();
        const response = await fetch(url, {
            method: 'DELETE',
            headers
        });

        if (!response.ok) {
            if (response.status === 401) {
                removeToken();
            }
            throw new Error(`DELETE request failed: ${response.statusText}`);
        }

        console.log('Resource deleted successfully');
        return await response.json() as T;
    } catch (error) {
        console.error('DELETE request error:', error);
        return undefined;
    }
}

// 添加登录方法
export async function login(username: string, password: string) {
    try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL || 'http://127.0.0.1:9988';
        const response = await fetch(`${baseURL}/v1/api/mark/account/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('登录失败');
        }

        const result = await response.json();
        if (result.code === 200 && result.data.access_token) {
            saveToken(result.data.access_token);
            return result;
        }
        
        throw new Error(result.message || '登录失败');
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
}

// 添加注册方法
export async function signup(username: string, password: string) {
    try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL || 'http://127.0.0.1:9988';
        const response = await fetch(`${baseURL}/v1/api/mark/account/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (!response.ok) {
            throw new Error('注册失败');
        }

        const result = await response.json();
        if (result.code === 200 && result.data.access_token) {
            saveToken(result.data.access_token);
            return result;
        }
        
        throw new Error(result.message || '注册失败');
    } catch (error) {
        console.error('Signup error:', error);
        throw error;
    }
}
