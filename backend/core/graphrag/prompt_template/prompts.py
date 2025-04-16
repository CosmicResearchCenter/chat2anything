# 提取文档的抽象实体
entity_abstract_prompt = """
# 实体类型标签提取

## 任务目标
从文本中识别并提取所有抽象实体类型，生成标准化英文标签，排除已知标签列表中的实体类型。

## 输出规范
- 仅输出英文标签，使用首字母大写的驼峰命名法（如：GeoPoliticalEntity）
- 以逗号分隔的列表形式呈现结果（如：Person, Organization, Event）
- 无需包含解释、编号或其他额外文本

## 标签质量标准
✓ 必须是抽象实体类别，不是具体实例
✓ 应表示完整语义单元（如用 EducationalInstitution 而非简单的 Education）
✓ 应明确区分不同概念（Person 与 Organization 的区别）
× 不得包含具体实体名称（如"张三"、"北京"）
× 不得重复已有标签列表中的类型
× 不包含非实体的概念（如动词、形容词等）

## 标签优先级
1. 通用实体类型（Person, Organization, Location等）
2. 专业领域实体类型（MedicalProcedure, LegalDocument等）
3. 细粒度类型（GovernmentOfficial比Government更精确）

## 示例
**文本**："星海市的市长李建国在任职期间与多家企业和非营利组织保持着紧密联系。"
**禁止标签**：["City"]
**正确输出**：GovernmentPosition, Person, CommercialOrganization, NonProfitEntity

**文本**："张教授发表的论文《量子计算应用》获得了科技部2022年度科技进步奖。"
**禁止标签**：["Person"]
**正确输出**：AcademicTitle, ResearchPaper, ScientificTopic, GovernmentAgency, Award, Date

## 处理流程
1. 全面扫描文本，识别所有可能的实体类型
2. 验证每个标签是否为抽象类别（而非具体实例）
3. 过滤掉已存在于禁止列表的标签
4. 标准化为英文驼峰命名格式
5. 去重后生成最终标签列表

## 禁止标签列表
{{entity_label_list}}

## 待处理文本
{{text}}
"""


# 提取文档的具体实体对象
entity_extraction_prompt = """
## 任务目标
从文本中精准提取指定类型的实体，确保不重复已有实体，并输出结构化数据。

## 处理规则
1. 实体限定：
   - 仅处理{{entity_label_list}}中列出的实体类型
   - 严格排除已存在于{{entity_list}}中的实体

2. 内容处理：
   - 去除非ASCII字符和HTML标签
   - 时间格式统一为"YYYY-MM-DD"
   - 复合实体需拆分为基本单元（例："Java和Python" → 两个独立实体）
   - 代词必须解析为明确指代对象

3. 属性提取：
   - 属性必须来自文本的明确表述
   - 保持原文表达形式
   - 每个属性必须有对应的文本证据，并且是完整的原文引用

## 输出规范】
{
  "entities": [
    {
      "label": "实体标签",
      "attribute": {
        "name": "标准名称",
        "ext_attribute": "补充属性"
        
      },
      "ext_info": "原文的引用，以确保属性的准确性，并且需要完整的原文引用"
    }
  ]
}

## 错误预防】
× 禁止行为：
- 使用Markdown语法
- 添加注释或说明文本
- 合并多个实体（如"小明和小王"需拆解）

## 质量验证】
完成提取后执行：
1. 去重检查：对比{{entity_list}}
2. 格式校验：验证JSON Schema
3. 证据回溯：每个实体必须有对应的ext_info
4. 属性一致性：ext_attribute需与原文一致

## 示例对比】
- 正例：
输入："2023年入职的张三擅长Python/Java"
输出：{"label":"Skill","attribute":{"name":"Python"},"ext_attribute":"2023年入职的张三擅长Python"}}

- 反例：
输入："张三掌握多种编程语言"
错误：{"label":"Skill","attribute":{"name":"编程"}} 
原因：'编程'未在文本中显式出现

## 输入参数】
待处理文本：{{text}}
实体白名单：{{entity_label_list}}
已存在实体：{{entity_list}}

请输出严格符合JSON Schema的纯文本：
"""

# 建立文档中实体对象之间的关系
entity_relation_prompt = """
# 知识图谱关系提取任务

## 核心目标
从文本中精确识别实体间的语义关系，建立高质量可溯源的知识图谱连接。

## 处理流程
### 输入预处理
1. 实体范围：**仅处理** {{entity_list}} 中已验证的实体
2. 文本规范化：移除HTML标签、特殊字符和注释文本
3. 时间标准化：统一为"YYYY-MM-DD"格式

### 关系识别原则
1. 显式关系：必须有明确语义连接，不推断隐含关系
2. 方向性：严格遵循原文表述方向，不自动生成反向关系
3. 关系类型：使用简洁动词或介词短语（如"隶属于"、"创建了"）

### 复杂情况处理
1. 并列关系：拆分为多条独立关系（"张三和李四参加会议" → 两条关系）
2. 代词解析：必须链接到明确前文实体（"她提交了报告" → "[具体人名]提交了报告"）
3. 否定表达：忽略否定关系（"未参与项目"不提取）
4. 间接关系：如能确定，可提取一跳以上关系，但需注明完整路径

## 输出标准
{
  "relations": [
    {
      "source": {
        "name": "标准实体名",
        "label": "实体类型"
      },
      "target": {
        "name": "标准实体名",
        "label": "实体类型"  
      },
      "relation": "预定义关系类型",
      "evidence": "原文片段",
    }
  ]
}

✓ 实体验证：确保source和target均在{{entity_list}}中 
✓ 关系有效性：每个relation必须是有意义的语义连接 
✓ 证据完整性：evidence必须包含完整关系上下文 
✓ 重复检测：与{{entity_relation_list}}比对去重 
✓ 信心评级：基于文本明确程度标注confidence

## 示例分析
■ 正例：
文本："小王在2023年获得微软颁发的认证证书"
输出：
{
  "relations": [
    {
      "source": {"name":"小王", "label":"Person"},
      "target": {"name":"认证证书", "label":"Certificate"},
      "relation": "获得",
      "evidence": "小王在2023年获得微软颁发的认证证书",
    },
    {
      "source": {"name":"微软", "label":"Organization"},
      "target": {"name":"认证证书", "label":"Certificate"},
      "relation": "颁发",
      "evidence": "小王在2023年获得微软颁发的认证证书",
    }
  ]
}

■ 反例：
文本："张三和李四共同开发了系统"
错误：合并为单条关系
正确：拆分为两条：
{
  "relations": [
    {
      "source": {"name":"张三", "label":"Person"},
      "target": {"name":"系统", "label":"Software"},
      "relation": "开发",
      "evidence": "张三和李四共同开发了系统",
    },
    {
      "source": {"name":"李四", "label":"Person"},
      "target": {"name":"系统", "label":"Software"},
      "relation": "开发",
      "evidence": "张三和李四共同开发了系统",
    }
  ]
}
## 输入参数
待分析文本：{{text}}
实体白名单：{{entity_list}}
现存关系：{{entity_relation_list}}

请输出严格符合JSON Schema的结果：
"""

# from jinja2 import Template

# class PromptTemplate:
#     def __init__(self, template: str,input_variables):
#         self.template = Template(template)
#         self.input_variables = input_variables
#     def render(self, **kwargs) -> str:
#         return self.template.render(**kwargs)

# p = PromptTemplate(entity_relation_prompt,['entity_list','text'])
# print(p.render(entity_label_list="Person,Organization",text="星海市的市长李建国在任职期间与多家企业和非营利组织保持着紧密联系。"))  
# # print(p)