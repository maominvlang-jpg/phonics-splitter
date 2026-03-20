# 自然拼读拆分skills
## 1.产品介绍
- Phonics Splitter 是一款专为英语自然拼读（Phonics）教学设计的自动化拆解工具。它能够接收任意英语单词，基于专业的语言学规则（3级规则体系）自动分析其拼读结构，并生成包含视觉引导、故事化讲解和标准发音的教学动画视频和规范的拆解原理和过程。
- 自然拼读skills PRD：https://my.feishu.cn/wiki/CthawLTD5imPkmknE1HcgqV6nEf?from=from_copylink
- 调研报告：https://my.feishu.cn/wiki/DBrqwOO5qiHVH8kRAYZcmDQKnWd?from=from_copylink
##  2. 制作背景
- 解决从朗读宝和纳米盒抓取到的数据匹配后缺少音频和自然拼读拆分，导致「AI背单词功能」无法正常使用的问题。
- <img width="640" height="287" alt="image" src="https://github.com/user-attachments/assets/5ae4dfdb-509a-498a-b6cf-fb1d5a56ea27" />
#### 特殊说明
```markdown
在自然拼读拆解过程中，可分为按「音节拆分」和按「词块 / 词根拆分」；
要读准、读顺单词 → 按 音节拆分（自然拼读）
要记意思、记拼写 → 按 词块 / 词根拆分（那是初中、高中才学的）
目前，AI背单词主要用于小学和初中，本skills的拆解主要是协助学生：学自然拼读 + 背单词拼写 + 记读音。
```
##  3.skills 和 MCP Server的区别
- 本项目分别包含一个skills和一个MCP Server，使用者可自行选择需要的
- 根据团队目前的AI工具使用情况，以下介绍皆以接入openclaw为核心展开

<table>
  <thead>
    <tr>
      <th>对比维度</th>
      <th>skills</th>
      <th>MCP Server</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>使用区别</strong></td>
      <td>
        - 安装到 OpenClaw 后，飞书机器人读规则分析单词<br>
        - 安装完成即可使用
      </td>
      <td>
        - 安装到 OpenClaw 后，飞书机器人直接调用工具<br>
        - 需要安装 MCP 依赖（见下文）
      </td>
    </tr>
    <!-- 合并单元格：支持内容 -->
    <tr>
      <td><strong>支持内容</strong></td>
      <td colspan="2">
        - ✅ 支持展示详细的拆分原理和过程；（全网独一份 😊😊😊）<br>
        - ✅ 支持生成单词各部分详细的拆分组成<br>
        - ✅ 支持生成「中英文拆分过程视频脚本」<br>
        - ✅ 支持在本地渲染并生成拆分过程视频<br>
        - ✅ 支持批量生成拆分数据
      </td>
    </tr>
    <tr>
      <td><strong>拆分准确性</strong></td>
      <td colspan="2">
        - 工具：MCP Server > skills<br>
        - 模型：Claude-Sonnet4.6 > gpt-oss-120b
      </td>
    </tr>
    <tr>
      <td><span style="color:red;"><strong>必做的</strong></span></td>
      <td colspan="2">
        - 必须在 <code>TOOLS.md</code> 中加入规则约束（见下文），否则 openclaw 会在拆解过程中自由发挥<br>
        - 必须在 <code>SOUL.md</code> 中加入规则约束（见下文），否则机器人会出现幻像和偷懒，直接跳步骤<br><br>
      </td>
    </tr>
    <tr>
      <td><strong>openclaw 输出的拆解过程</strong></td>
      <td colspan="2">
        <img width="614" height="606" alt="image" src="https://github.com/user-attachments/assets/2d9650db-97c9-424f-9239-3b489dea90dc" />
        <img width="428" height="622" alt="image" src="https://github.com/user-attachments/assets/a7254b0c-ea3b-4bda-9dde-eb03be7fa073" />
        <img width="583" height="613" alt="image" src="https://github.com/user-attachments/assets/d9126f16-e643-4ada-80d8-65483922b14d" />
    </tr>
  </tbody>
</table>
