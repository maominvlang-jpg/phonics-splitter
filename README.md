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
    <tr>
      <td><strong>生成的视频质量</strong></td>
      <td colspan="2">
        <ul>
          <li>音视频同步的准确性：编译器 > 本地终端
            <ul style="list-style-type: circle; margin-left: 20px;">
              <li>原因：
                <ul style="list-style-type: square; margin-left: 20px;">
                  <li>部分单词在本地渲染时无法获取到对应的图片；</li>
                  <li>本地终端视频的 ffmpeg 时序计算不够精准——音频偏移量是按固定时间估算的，和实际动画帧数有出入。</li>
                </ul>
              </li>
            </ul>
          </li>
          <li>视频的精美程度：本地终端 > 编译器
            <ul style="list-style-type: circle; margin-left: 20px;">
              <li>（暂时没搞懂为什么）</li>
            </ul>
          </li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

##  4.TOOL.md配置修改
- 必须添加：直接复制粘贴下方规则即可
```markdown
Phonics Splitter Rules
⚠️ CRITICAL INSTRUCTION: STRICT ADHERENCE REQUIRED
When calling, executing, or simulating the phonics-splitter skill (located at /root/.openclaw/workspace-Monica/skills/phonics-splitter/), you must STRICTLY follow the rules defined in: skills/phonics-splitter/SKILL.md
You are NOT allowed to:
Improvise or change the logic based on your pre-trained knowledge.
Skip any of the 7 steps (Step 0 to Step 7). Step 0 (IPA 查询) MUST be executed first.
Fabricate letters or consonants that do not exist in the original word.
Omit the pre-output self-checklist.
Alter the output format or animation JSON schema. You MUST output all 6 mandatory items.
You MUST:
Execute steps in exact order: 0→1→2→3→4→5→6→7.
Explicitly list the indices of the letters when applying rules to prevent hallucination.
Perform the "Self-Check List" before outputting.
Use the exact "Animal Rules" (Rabbit, Tiger, Camel, Lion, Turtle) as defined.
```

##  5.SOUL.md配置修改
- 必须添加：直接复制粘贴下方规则即可
```markdown
强制遵守指令 ：
当使用任何 skill （特别是 phonics-splitter ）时， 绝对禁止 使用通用预训练知识来替代技能文档中的规则。必须 100% 严格执行 技能文档（如 SKILL.md ）中的每一个步骤和输出格式要求，绝不跳步或捏造数据。
```
##  6.本地终端环境配置
- 不想生成视频的话，以下步骤都可以省略
- 第一步：安装 Homebrew（如果没有）
  ```markdown
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ``` 
- 第二步：安装 ffmpeg
  ```markdown
  brew install ffmpeg
  ``` 
- 第三步：在虚拟环境中安装 Python 依赖
  ```markdown
  # （1）：创建虚拟环境（只需做一次）
  python3 -m venv ~/phonics-env

  # （2）：激活虚拟环境
  source ~/phonics-env/bin/activate

  # （3）：安装依赖（激活后 pip 就可以直接用了）
  pip install manim edge-tts requests pillow
  激活成功后，终端最左边会出现 `(phonics-env)` 的前缀，之后每次打开终端想用的时候，重新执行第二步激活一下就好。
  ```
- 第四步：验证安装
  ```markdown
  #正常应该输出版本号
  pip3 show manim 
  manim --version
  ``` 
  
##  7.本地终端环境配置  
- 激活虚拟环境——>复制粘贴openclw输出的「本地渲染指引」——>回车等待视频生成
- 到终端给的地址里找生成的视频
- 
  <img width="580" height="545" alt="image" src="https://github.com/user-attachments/assets/a6d5d44c-5267-4b94-a5f5-7bfe47cf2621" />
  <img width="580" height="497" alt="image" src="https://github.com/user-attachments/assets/03a38856-c13c-4e87-832d-6707ca1c10d4" />
  <img width="580" height="497" alt="image" src="https://github.com/user-attachments/assets/ab28c66b-3504-4910-8602-0e563bfafe5f" />

##  8.安装MCP Server依赖
- 如果使用的是skills，无需这一步
- 第一步：进服务器，建虚拟环境并安装依赖
- 第二步：确认路径正确
- 第三步：验证 MCP Server 能否正常启动
- 第四步：配置到openclaw
- 第五步：重启 OpenClaw
