#!/bin/bash
# ============================================
# 学习通作业提取工具 - APK构建脚本
# 在 WSL Ubuntu 中运行此脚本
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
KEYSTORE_PASSWORD="${XXT_KEYSTORE_PASSWORD:-xxtdocx-$(date +%s)}"

echo "========================================="
echo "  学习通作业提取工具 - APK 构建脚本"
echo "  Xxt-Docx-Exporter v1.0.0"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── 1. Install system dependencies ──
echo -e "${YELLOW}[1/6] 安装系统依赖...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq \
    python3 python3-pip python3-dev \
    openjdk-17-jdk \
    git autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev \
    autoconf automake libtool \
    build-essential lld \
    2>&1 | tail -3

echo -e "${GREEN}系统依赖安装完成${NC}"

# ── 2. Install Buildozer ──
echo -e "${YELLOW}[2/6] 安装 Buildozer...${NC}"
pip3 install --upgrade buildozer Cython 2>&1 | tail -3
echo -e "${GREEN}Buildozer 安装完成${NC}"

# ── 3. Copy project files ──
echo -e "${YELLOW}[3/6] 准备项目文件...${NC}"

# Create a temporary build directory
BUILD_DIR="/tmp/xxt_build_$$"
mkdir -p "$BUILD_DIR"
cp -r "$SCRIPT_DIR"/* "$BUILD_DIR/"
cp -r "$PROJECT_DIR/my_xxt" "$BUILD_DIR/"
cp -r "$PROJECT_DIR/img" "$BUILD_DIR/"
cp "$PROJECT_DIR/config.py" "$BUILD_DIR/"
cp "$PROJECT_DIR/answers" "$BUILD_DIR/answers" 2>/dev/null || mkdir -p "$BUILD_DIR/answers"

# Create __init__.py for my_xxt
touch "$BUILD_DIR/my_xxt/__init__.py"

# Copy cover image to build dir img/
mkdir -p "$BUILD_DIR/img"
cp "$PROJECT_DIR/img/cover.jpg" "$BUILD_DIR/img/" 2>/dev/null

echo -e "${GREEN}项目文件准备完成${NC}"

# ── 4. Check keystore ──
echo -e "${YELLOW}[4/6] 检查签名密钥...${NC}"
if [ ! -f "$BUILD_DIR/xxtdocx.keystore" ]; then
    echo -e "${YELLOW}生成新的签名密钥...${NC}"
    keytool -genkey -v \
        -keystore "$BUILD_DIR/xxtdocx.keystore" \
        -alias xxtdocx \
        -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass "$KEYSTORE_PASSWORD" -keypass "$KEYSTORE_PASSWORD" \
        -dname "CN=liuwanwan1, OU=Dev, O=XxtDocx, L=Beijing, ST=Beijing, C=CN"
fi
echo -e "${GREEN}签名密钥就绪${NC}"

# ── 5. Build APK ──
echo -e "${YELLOW}[5/6] 开始构建 APK (这可能需要 20-40 分钟)...${NC}"
cd "$BUILD_DIR"

# First build - generates debug APK
buildozer -v android debug 2>&1 | tail -20

# Then build release APK
buildozer -v android release 2>&1 | tail -20

echo -e "${GREEN}APK 构建完成${NC}"

# ── 6. Collect artifacts ──
echo -e "${YELLOW}[6/6] 收集构建产物...${NC}"
ARTIFACT_DIR="$PROJECT_DIR/release"
mkdir -p "$ARTIFACT_DIR"

# Find and copy APK
APK_FILE=$(find "$BUILD_DIR/bin" -name "*.apk" 2>/dev/null | head -1)
if [ -f "$APK_FILE" ]; then
    cp "$APK_FILE" "$ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk"
    echo -e "${GREEN}APK 已复制到: $ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk${NC}"
    ls -lh "$ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk"
else
    # Check for unsigned release APK
    APK_FILE=$(find "$BUILD_DIR/bin" -name "*release-unsigned*.apk" 2>/dev/null | head -1)
    if [ -f "$APK_FILE" ]; then
        # Sign with jarsigner
        echo -e "${YELLOW}签名 APK...${NC}"
        jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
            -keystore "$BUILD_DIR/xxtdocx.keystore" \
            -storepass "$KEYSTORE_PASSWORD" -keypass "$KEYSTORE_PASSWORD" \
            "$APK_FILE" xxtdocx

        # Align with zipalign
        ANDROID_SDK=$(find ~/.buildozer -name "build-tools" -type d 2>/dev/null | head -1)
        if [ -d "$ANDROID_SDK" ]; then
            ZIPALIGN=$(find "$ANDROID_SDK" -name "zipalign" -type f 2>/dev/null | head -1)
            if [ -f "$ZIPALIGN" ]; then
                "$ZIPALIGN" -v 4 "$APK_FILE" "$ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk"
            else
                cp "$APK_FILE" "$ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk"
            fi
        else
            cp "$APK_FILE" "$ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk"
        fi
        echo -e "${GREEN}签名完成: $ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk${NC}"
        ls -lh "$ARTIFACT_DIR/xxt-docx-exporter-v1.0.0.apk"
    else
        echo -e "${RED}未找到 APK 文件${NC}"
        echo "Build directory contents:"
        find "$BUILD_DIR/bin" -type f 2>/dev/null || echo "(empty)"
    fi
fi

# Cleanup
rm -rf "$BUILD_DIR"

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  构建完成!${NC}"
echo -e "${GREEN}  APK 位置: $ARTIFACT_DIR/${NC}"
echo -e "${GREEN}=========================================${NC}"
