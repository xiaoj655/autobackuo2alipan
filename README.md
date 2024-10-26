![logo.png](https://img.alicdn.com/imgextra/i3/O1CN01qcJZEf1VXF0KBzyNb_!!6000000002662-2-tps-384-92.png)

# 这是什么? 

把本地文件上传到阿里云盘的工具, 未来会有web页面可视化支持, __目前仅支持命令行操作__

# 使用

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 配置阿里云盘应用, 在 `src/config/global.yml` 文件中配置阿里云盘应用密钥和应用ID

3. 配置要 __备份__ 的文件夹, 在 `src/config/backup.yml` 文件中配置要备份的文件夹路径
- frequency: 备份频率, 可选值: 1d, 1w, 1m, 1y, 1h
- compress_type: 压缩类型, 可选值: .tar.gz, .tar, .zip
- 以及相关账户和密码

# 运行

```bash
cd src
python scripts/immediate_backup.py
```

## 更推荐您使用 `crontab` 定时运行


### 处于开发阶段, 请勿用于生产环境, 作者还在努力开发中🥲