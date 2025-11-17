# Streamlit Cloud 部署问题排查

## 当前错误
```
ModuleNotFoundError: No module named 'openai'
File "/mount/src/language-art/stramlit project.py", line 3
```

## 解决方案

### 1. 确保 requirements.txt 在正确位置

根据错误路径 `/mount/src/language-art/stramlit project.py`，说明：
- GitHub 仓库名是 `language-art`
- 主文件 `stramlit project.py` 在仓库根目录

**因此，`requirements.txt` 必须在 GitHub 仓库的根目录！**

### 2. requirements.txt 内容

确保根目录的 `requirements.txt` 包含：

```txt
streamlit>=1.0.0
openai>=1.0.0
```

### 3. 检查 GitHub 仓库结构

你的 GitHub 仓库应该类似这样：

```
language-art/
├── requirements.txt          ← 必须在这里！
├── stramlit project.py       ← 主文件
└── .streamlit/              (可选，用于本地开发)
    └── secrets.toml.example
```

### 4. 在 Streamlit Cloud 配置

1. **Main file path**: `stramlit project.py` (如果文件在根目录)
   或 `streamlit project/stramlit project.py` (如果文件在子目录)

2. **Secrets**: 添加以下内容
   ```toml
   [openai]
   api_key = "your-api-key-here"
   ```

### 5. 验证步骤

1. ✅ 检查 GitHub 仓库根目录是否有 `requirements.txt`
2. ✅ 检查 `requirements.txt` 是否包含 `openai>=1.0.0`
3. ✅ 检查 Streamlit Cloud 的 "Main file path" 是否正确
4. ✅ 检查 Streamlit Secrets 是否已配置

### 6. 如果仍然报错

1. 在 Streamlit Cloud 点击 "Manage app" → "Settings"
2. 检查 "Main file path" 是否正确
3. 查看 "Logs" 查看详细错误信息
4. 尝试重新部署应用

## 常见问题

**Q: 为什么需要 requirements.txt 在根目录？**
A: Streamlit Cloud 会在项目根目录查找 `requirements.txt` 文件来安装依赖。

**Q: 可以有两个 requirements.txt 吗？**
A: 可以，但 Streamlit Cloud 只会使用根目录的那个。

**Q: 文件名中的空格会有问题吗？**
A: 通常不会有问题，但建议重命名为 `streamlit_project.py` 以避免潜在问题。

