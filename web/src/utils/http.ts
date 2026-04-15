// http.ts

// 移除 localStorage 相关的 token 存储函数，改用 httpOnly cookie
// 保留空函数以保持向后兼容，但实际上不再使用 localStorage
export const saveToken = (token: string) => {
    // 不再使用 localStorage 存储 token，改为依赖 httpOnly cookie
    console.warn('saveToken is deprecated, using httpOnly cookie instead');
};

export const getToken = () => {
    // 不再从 localStorage 获取 token，改为依赖 httpOnly cookie
    console.warn('getToken is deprecated, using httpOnly cookie instead');
    return null;
};

export const removeToken = () => {
    // 不再从 localStorage 移除 token，改为调用后端 logout 接口
    console.warn('removeToken is deprecated, use logout() instead');
};

// 新增：登出方法
export async function logout() {
    try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL || 'http://127.0.0.1:9988';
        const response = await fetch(`${baseURL}/v1/api/mark/account/logout`, {
            method: 'POST',
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('登出失败');
        }

        return await response.json();
    } catch (error) {
        console.error('Logout error:', error);
        throw error;
    }
}

// 新增：获取认证请求头 - 现在返回空对象，因为 token 由 cookie 自动携带
const getAuthHeaders = (customHeaders?: any) => {
    // 不再需要手动添加 Authorization header，因为 token 由 cookie 自动携带
    return customHeaders ? { ...customHeaders } : {};
};

export async function getRequest<T>(url: string): Promise<T | undefined> {
    try {
        const headers = getAuthHeaders();
        const response = await fetch(url, {
            method: 'GET',
            headers,
            credentials: 'include',
        });

        if (!response.ok) {
            if (response.status === 401) {
                // 401 时不再需要手动清除 token，cookie 会在登出时清除
            }
            throw new Error(`GET request failed: ${response.statusText}`);
        }

        return await response.json() as T;
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
            credentials: 'include',
        });

        if (!response.ok) {
            if (response.status === 401) {
                // 401 时不再需要手动清除 token
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
            credentials: 'include',
        });

        if (!response.ok) {
            if (response.status === 401) {
                // 401 时不再需要手动清除 token
            }
            throw new Error(`PUT request failed: ${response.statusText}`);
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            return await response.json() as T;
        }

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
            headers,
            credentials: 'include',
        });

        if (!response.ok) {
            if (response.status === 401) {
                // 401 时不再需要手动清除 token
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
            body: JSON.stringify({ username, password }),
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('登录失败');
        }

        const result = await response.json();
        if (result.code === 200) {
            // 不再手动保存 token，依赖 httpOnly cookie
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
            body: JSON.stringify({ username, password }),
            credentials: 'include',
        });

        if (!response.ok) {
            throw new Error('注册失败');
        }

        const result = await response.json();
        if (result.code === 200) {
            // 不再手动保存 token，依赖 httpOnly cookie
            return result;
        }
        
        throw new Error(result.message || '注册失败');
    } catch (error) {
        console.error('Signup error:', error);
        throw error;
    }
}

// 添加管理员注册方法
export async function signupAdmin(username: string, password: string, adminKey: string) {
    try {
        const baseURL = import.meta.env.VITE_APP_BASE_URL || 'http://127.0.0.1:9988';
        const response = await fetch(`${baseURL}/v1/api/mark/account/signup_admin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, admin_key: adminKey }),
            credentials: 'include',
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '管理员注册失败');
        }

        const result = await response.json();
        if (result.code === 200) {
            // 不再手动保存 token，依赖 httpOnly cookie
            return result;
        }
        
        throw new Error(result.message || '管理员注册失败');
    } catch (error) {
        console.error('Admin Signup error:', error);
        throw error;
    }
}
