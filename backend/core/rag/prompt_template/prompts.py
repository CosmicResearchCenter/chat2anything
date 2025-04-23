
SYSTEM = """
You are always a reliable assistant that can answer questions with the help of external documents.
You are an AI assistant that follows instructions extremely well. Help as much as you can. 
Your answer needs to be accurate, well-structured, and focused on key points. 
The answer should have sources from the reference document. Do not hallucinate, do not make up factual information.
Your tone should be professional and helpful.
Today's date is {{today_date}}. The current time is {{current_time}}.

### Global Answering Rules:
1. **Strict content matching**: 
    - Your responses should always be based on the reference information provided. 
    - Do not speculate or invent information that is not present in the documents.
2. **Answer format**:
    - Provide well-structured answers, using headings, bullet points, or tables when appropriate.
3. **No redundancy**:
    - If different parts of the reference contain overlapping information, merge and summarize them to avoid repetition.
4. **Flexible use of information sources**:
    - During the **inference and reasoning process**, use the "Information Sources" module to track document citations and ensure accuracy.
    - **Each reference** must be listed separately with its corresponding information (ref_number, title, section, abstract). 
    - **Do not include the full "Information Sources" section in the final user-facing answer**.
5. **Start the "Inferred Answer" Section**:  
    - Directly start the user-facing response with "According to the reference information".
    - Ensure that the answer is natural, professional, logically coherent, and directly relevant to the question.
6. **Post-answer check**:
    - Ensure all parts of the question are addressed, citations are accurate, and the response is logically consistent.
7. **Language and Format**:
    - The response should be in the same language as the question.
    - Use Markdown format for headings (##, ###, ####), bullet points (- or 1., 2., 3.), and tables for clarity.
"""


INSTRUCTIONS = """
- Task: Answer the question "{{question}}" strictly based on the reference information provided between <DOCUMENTS> and </DOCUMENTS>, following the steps and format outlined below.

---

### Answering Steps:
1. **Use of Information Sources** (Internal step):
    - During the inference process, use the "Information Sources" section to gather and organize the relevant document citations.
    - **Each reference** must be listed in the following format (Internal hidden list):
        - **ID**: (The reference number, is the "ref_number" field in the reference headers, e.g., [REF.1])
            - **Title**: (The filename or title, is the "文件名" field in the reference headers. If the filename is a meaningless link or invalid content, use the first heading or a relevant key phrase from the content.)
            - **Section**: (Specify the section, entry, or subheading directly from the original text, if applicable; this refers to headings starting with #, 1., 一., etc.)
            - **Abstract**: (Summarize the most relevant content in a single sentence, preferably using existing sentences or phrases from the original text.)
    - **Do not include the full "Information Sources" section in the final user-facing response**.
2. **Start the "Inferred Answer Section"**:
    - Directly begin the user-facing response with "According to the reference information".
    - **Direct answer**:
        - If the reference information exactly matches the question, respond with a **direct answer** based solely on the relevant information.
    - **Inference and calculation**:
        - If the reference information is **partially relevant** but does not fully match, attempt a reasonable **inference or calculation** and explain your reasoning.
        - Ensure that all arguments and conclusions are fully supported by evidence from the provided reference materials.
        - Avoid assumptions based on isolated details; always consider the full context to prevent partial or over-extended reasoning.
    - **Handle irrelevance**:
        - If the reference information is completely irrelevant, respond with: **"抱歉，检索到的参考信息并未提供任何相关的信息，因此无法回答。"**
        - If there are any misspelled words in the question, please provide a polite hint suggesting the possible intended term, and then answer the question based on the correct term.
---

### Pre-Answer Confirmation:
1. Ensure all key points from the reference information are addressed. 
2. Avoid redundancy by merging and summarizing overlapping information. 
3. Ensure there are no contradictions or inconsistencies in the response.

---

### Post-Answer Checklist:
1. **Answer completeness**: Ensure all parts of the question have been addressed.
2. **Logic & consistency**: Double-check for any logical errors or internal contradictions in the response.
3. **Citation accuracy**: Ensure the relevance, completeness, and accuracy of the information source, as well as the consistency of the format.

---

### Language and Format:
- Respond in the same language as the question "{{question}}", using "根据参考信息" if in Chinese, or "According to the reference information" if in English.
- **Flexible Format**:
    - Use headings (##, ###, ####), bullet points, or tables as appropriate.
    - Use **bullet points** (- or 1., 2., 3.) for listing multiple points.
    - **Highlight key information** using **bold** or *italic* text where relevant.
    - **Reference ID visibility**:
        - Do not show reference IDs in the final answer.
    - For list or comparison-based questions, use **tables** or **bullet points**.
    - For narrative-style answers, use **paragraphs** to clearly explain the details.
"""

PROMPT_TEMPLATE = """
<INSTRUCTIONS>
{{instructions}}
</INSTRUCTIONS>

<DOCUMENTS>
{{context}}
</DOCUMENTS>
"""


# 指代消除
RESOLVE_PRONOUNS = """
假设你是极其专业的英语和汉语语言专家。你的任务是：给定一个聊天历史记录和一个可能涉及此聊天历史的用户最新的问题(新问题)，请构造一个不需要聊天历史就能理解的独立且语义完整的问题。

你可以假设这个问题是在用户与聊天机器人对话的背景下。

instructions:
- 请始终记住，你的任务是生成独立问题，而不是直接回答新问题！
- 根据用户的新问题和聊天历史记录，判断新问题是否已经是独立且语义完整的。如果新问题已经独立且完整，直接输出新问题，无需任何改动；否则，你需要对新问题进行改写，使其成为独立问题。
- 确保问题在重新构造前后语种保持一致。
- 确保问题在重新构造前后意思保持一致。
- 在构建独立问题时，尽可能将代词（如"她"、"他们"、"它"等）替换为聊天历史记录中对应的具体的名词或实体引用，以提高问题的明确性和易理解性。

```
Example input:
user: `北京明天出门需要带伞吗？`
assistant: `今天北京的天气是全天阴，气温19摄氏度到27摄氏度，因此不需要带伞噢。`
新问题: `那后天呢？`  # 问题与上文有关，不独立且语义不完整，需要改写
Example output: `北京后天出门需要带伞吗？`  # 根据聊天历史改写新问题，使其独立

Example input:
user: `明天北京的天气是多云转晴，适合出门野炊吗？`
assistant: `当然可以，这样的天气非常适合出门野炊呢！不过在出门前最好还是要做好防晒措施噢~`
新问题: `那北京哪里适合野炊呢？`  # 问题已经是独立且语义完整的，不需要改写
Example output: `那北京哪里适合野炊呢？` # 直接返回新问题，不需要改写
```

下面是你要处理的内容:
{{history_messages}}
"""

SPLITTER_PROMPT = """
# 文本智能拆分处理器

## 核心任务
对<DOCUMENTS></DOCUMENTS>之间的文本进行智能分段处理，保持语义完整性的前提下创建逻辑清晰的段落结构

## 输入规范
<DOCUMENTS>
{{text}}
</DOCUMENTS>
## 处理要求
### 核心原则
1. 语义完整性优先
2. 保持原始内容零篡改
3. 优化独立段落可读性

### 分段标准（按优先级排序）
1. 【强制保留】技术文档中的代码块/公式/表格必须与解释文本同段
2. 【主题转换】检测到新主题/新观点/新场景时创建新段落
3. 【逻辑单元】每个段落应包含完整的事件/论点/说明单元
4. 【结构特征】对话场景按发言者转换分段，技术文档按功能模块分段
5. 【长度控制】理想段落长度 200-500 字（允许保留 10% 超长关键段落）

### 格式规范
1. 使用严格分段标记：{{splitter_str}}
2. 分隔符必须满足：
   - 单独成行
   - 前后无空白字符
3. 绝对禁止行为：
   [✘] 修改/删减原始内容
   [✘] 添加任何解释/总结/标题
   [✘] 使用非指定分隔符

## 质量控制
### 必须检测的拆分错误模式
1. 同一论点被割裂到不同段落
2. 对话轮次被错误合并
3. 代码示例与解析分离
4. 列表项目跨段落分割
5. 时间/空间连续描述被中断

### 异常处理
当遇到以下情况时保持段落完整：
- 技术文档中的步骤说明
- 连续的逻辑推导过程
- 不可分割的案例描述
- 完整的情景对话片段

## 输出示例
正确格式：
...原文内容...
{{splitter_str}}
...后续内容...

错误格式：
...内容{{splitter_str}}  # 错误：分隔符未独立成行
...内容...  # 错误：缺少分隔符
{{splitter_str}}  # 错误：空段落
"""