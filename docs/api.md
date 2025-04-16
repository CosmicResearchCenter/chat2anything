# Chat2anything API 接口文档

## 目录

1. 账户相关
2. 知识库相关
3. 聊天相关
4. 管理员相关

## 账户相关

### 用户注册（POST）

URL：`http://{your_host}:9988/v1/api/mark/account/signup`

#### 请求参数（Body）

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| username | "test_user" | 是 | String | 用户名 |
| password | "password123" | 是 | String | 密码 |

#### 请求示例

```python
import requests
import json

url = "http://{your_host}:9988/v1/api/mark/account/signup"
headers = {
    "Content-Type": "application/json"
}
data = {
    "username": "test_user",
    "password": "password123"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "message": "Sign Up Successful"
}
```

### 用户登录（POST）

URL：`http://{your_host}:9988/v1/api/mark/account/login`

#### 请求参数（Body）

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| username | "test_user" | 是 | String | 用户名 |
| password | "password123" | 是 | String | 密码 |

#### 请求示例

```python
import requests
import json

url = "http://{your_host}:9988/v1/api/mark/account/login"
headers = {
    "Content-Type": "application/json"
}
data = {
    "username": "test_user",
    "password": "password123"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "message": "Login Successful"
}
```

### 获取当前用户信息（GET）

URL：`http://{your_host}:9988/v1/api/mark/account/me`

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests

url = "http://{your_host}:9988/v1/api/mark/account/me"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)
```

#### 响应示例

```
test_user
```

## 知识库相关

### 创建知识库（POST）

URL：`http://{your_host}:9988/v1/api/mark/knowledgebase/`

#### 请求参数（Body）

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| base_name | "技术文档" | 是 | String | 知识库名称 |

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests
import json

url = "http://{your_host}:9988/v1/api/mark/knowledgebase/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
data = {
    "base_name": "技术文档"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "message": "获取成功",
  "code": 200,
  "data": [
    {
      "knowledgeBase_id": "kb12345"
    }
  ]
}
```

### 获取知识库列表（GET）

URL：`http://{your_host}:9988/v1/api/mark/knowledgebase/`

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests

url = "http://{your_host}:9988/v1/api/mark/knowledgebase/"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "message": "获取成功",
  "code": 200,
  "data": [
    {
      "id": "kb12345",
      "docs_num": 3,
      "related_conversations": 5,
      "knowledgeBaseName": "技术文档"
    },
    {
      "id": "kb67890",
      "docs_num": 1,
      "related_conversations": 2,
      "knowledgeBaseName": "产品手册"
    }
  ]
}
```

### 上传文档到知识库（PUT）

URL：`http://{your_host}:9988/v1/api/mark/knowledgebase/{base_id}`

#### 路径参数

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| base_id | "kb12345" | 是 | String | 知识库ID |

#### 表单参数

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| file | [文件] | 是 | File | 要上传的文档文件 |

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests

url = "http://{your_host}:9988/v1/api/mark/knowledgebase/kb12345"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
files = {
    "file": open("document.pdf", "rb")
}

response = requests.put(url, headers=headers, files=files)

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "message": "上传成功",
  "code": 200,
  "data": [
    {
      "doc_id": "doc123",
      "index_status": "pending",
      "knowledgeBaseId": "kb12345"
    }
  ]
}
```

### 插入文档到知识库（POST）

URL：`http://{your_host}:9988/v1/api/mark/knowledgebase/{base_id}/doc/{doc_id}/index`

#### 路径参数

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| base_id | "kb12345" | 是 | String | 知识库ID |
| doc_id | "doc123" | 是 | String | 文档ID |

#### 请求参数（Body）

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| splitter_model | 1 | 是 | Integer | 分割模型类型 |
| splitter_args | {"chunk_size": "1000", "chunk_overlap": "200"} | 是 | Object | 分割参数 |

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests
import json

url = "http://{your_host}:9988/v1/api/mark/knowledgebase/kb12345/doc/doc123/index"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
data = {
    "splitter_model": 1,
    "splitter_args": {
        "chunk_size": "1000",
        "chunk_overlap": "200"
    }
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "message": "正在建立索引",
  "code": 200,
  "data": [
    {
      "knowledgeBaseId": "kb12345",
      "doc_id": "doc123",
      "index_status": "indexing"
    }
  ]
}
```

## 聊天相关

### 创建会话（POST）

URL：`http://{your_host}:9988/v1/api/mark/chat/create-conversation`

#### 请求参数（Body）

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| knowledge_base_id | "kb12345" | 是 | String | 知识库ID |

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests
import json

url = "http://{your_host}:9988/v1/api/mark/chat/create-conversation"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
data = {
    "knowledge_base_id": "kb12345"
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "data": {
    "id": 123,
    "num_conversation": 0,
    "knowledgeBaseId": "kb12345",
    "username": "test_user",
    "conversationName": "New Conversation",
    "lastChatTime": "2025-04-16T10:30:00",
    "delete_sign": false
  },
  "code": 200,
  "message": "Create conversation successfully!"
}
```

### 发送聊天消息（POST）

URL：`http://{your_host}:9988/v1/api/mark/chat/chat-message`

#### 请求参数（Body）

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| conversation_id | "123" | 是 | String/Int | 对话ID |
| message | "如何使用API?" | 是 | String | 聊天消息内容 |
| streaming | false | 否 | Boolean | 是否使用流式响应，默认为false |

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests
import json

url = "http://{your_host}:9988/v1/api/mark/chat/chat-message"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
data = {
    "conversation_id": "123",
    "message": "如何使用API?",
    "streaming": false
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "data": ["根据您的问题，API使用方法如下：..."],
  "code": 200,
  "message": "Get chat message successfully!"
}
```

**注意**：如果streaming参数设为true，将返回流式响应。

### 获取聊天历史（GET）

URL：`http://{your_host}:9988/v1/api/mark/chat/chat-history/{conversation_id}`

#### 路径参数

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| conversation_id | "123" | 是 | String | 对话ID |

#### 请求头

```
Authorization: Bearer {access_token}
```

#### 请求示例

```python
import requests

url = "http://{your_host}:9988/v1/api/mark/chat/chat-history/123"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "data": [
    {
      "conversation_id": "123",
      "query": "如何使用API?",
      "answer": "根据您的问题，API使用方法如下：...",
      "current_knowledge_baseid": "kb12345",
      "retriever_docs": [
        {
          "content": "API使用说明...",
          "knowledge_doc_name": "API文档.pdf",
          "knowledgeBaseId": "kb12345"
        }
      ]
    }
  ],
  "code": 200,
  "message": "Get chat history successfully!"
}
```

## 管理员相关

### 获取系统信息（GET）

URL：`http://{your_host}:9988/v1/api/mark/admin/system_info`

#### 请求头

```
Authorization: Bearer {access_token}  # 需要管理员权限
```

#### 请求示例

```python
import requests

url = "http://{your_host}:9988/v1/api/mark/admin/system_info"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "code": 200,
  "message": "返回系统基本信息",
  "data": [
    {
      "knowledge_base_count": 10,
      "user_count": 25,
      "conversation_count": 150
    }
  ]
}
```

### 获取所有用户（GET）

URL：`http://{your_host}:9988/v1/api/mark/admin/users`

#### 请求头

```
Authorization: Bearer {access_token}  # 需要管理员权限
```

#### 请求示例

```python
import requests

url = "http://{your_host}:9988/v1/api/mark/admin/users"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "code": 200,
  "message": "返回用户对话信息",
  "data": [
    [
      {
        "username": "test_user",
        "admin_sign": false
      },
      {
        "username": "admin_user",
        "admin_sign": true
      }
    ]
  ]
}
```

### 授予用户管理员权限（POST）

URL：`http://{your_host}:9988/v1/api/mark/admin/grant_admin/{username}`

#### 路径参数

| 参数名 | 示例参数值 | 是否必填 | 参数类型 | 描述说明 |
| ------ | ---------- | -------- | -------- | -------- |
| username | "test_user" | 是 | String | 要授权的用户名 |

#### 请求头

```
Authorization: Bearer {access_token}  # 需要管理员权限
```

#### 请求示例

```python
import requests

url = "http://{your_host}:9988/v1/api/mark/admin/grant_admin/test_user"
headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

response = requests.post(url, headers=headers)

print(response.status_code)
print(response.text)
```

#### 响应示例

```json
{
  "code": 200,
  "message": "授予用户管理员权限成功",
  "data": []
}
