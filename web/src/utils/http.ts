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

// 注册用户 - 更新为支持邀请码和邮箱
export async function signup(username: string, password: string, inviteCode?: string, email?: string): Promise<any> {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const requestData: any = {
    username,
    password
  };
  
  if (inviteCode) {
    requestData.invite_code = inviteCode;
  }
  
  if (email) {
    requestData.email = email;
  }
  
  const response = await postRequest<any>(baseURL + '/v1/api/mark/account/signup', requestData);
  
  if (response.code === 200) {
    // 注册成功后自动登录
    const token = response.data.access_token;
    localStorage.setItem('token', token);
    return response;
  } else {
    throw new Error(response.message || '注册失败');
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
            body: JSON.stringify({ username, password, admin_key: adminKey })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '管理员注册失败');
        }

        const result = await response.json();
        if (result.code === 200 && result.data.access_token) {
            saveToken(result.data.access_token);
            return result;
        }
        
        throw new Error(result.message || '管理员注册失败');
    } catch (error) {
        console.error('Admin Signup error:', error);
        throw error;
    }
}

// 邀请码管理相关API

// 生成邀请码
export async function generateInviteCode(data: {
  max_uses?: number;
  expire_hours?: number;
  description?: string;
}): Promise<any> {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  return await postRequest<any>(baseURL + '/api/admin/generate_invite_code', data);
}

// 获取邀请码列表
export async function getInviteCodes(page: number = 1, pageSize: number = 20): Promise<any> {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString()
  });
  return await getRequest<any>(baseURL + `/api/admin/invite_codes?${params.toString()}`);
}

// 更新邀请码
export async function updateInviteCode(id: number, data: {
  is_active?: boolean;
  description?: string;
  max_uses?: number;
}): Promise<any> {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  return await putRequest<any>(baseURL + `/api/admin/invite_code/${id}`, data);
}

// 删除邀请码
export async function deleteInviteCode(id: number): Promise<any> {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  return await deleteRequest<any>(baseURL + `/api/admin/delete_invite_code/${id}`);
}

// 获取邀请码统计信息
export async function getInviteCodeStats(): Promise<any> {
  const baseURL = import.meta.env.VITE_APP_BASE_URL;
  return await getRequest<any>(baseURL + '/api/admin/invite_code_stats');
}
