# btc_analysis
## btc多因子分析

### 环境部署步骤

1. **创建虚拟环境**：
   使用 `uv` 管理包创建虚拟环境。首先，确保安装了 `uv`。然后，执行以下命令创建虚拟环境：
   
   uv create myenv
   
这将创建一个名为 myenv 的虚拟环境。

2. **激活虚拟环境** ：激活虚拟环境以便后续操作使用该环境的依赖。

   source myenv/bin/activate

4. **安装依赖** ：使用 pip 安装项目所需的依赖。

   uv pip install -r requirements.txt

6. **运行项目** ：
7. 
   uv run server.py

8. **访问项目** ：
    在浏览器中访问 http://localhost:5000 ，查看应用运行情况。
