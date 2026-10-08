FROM python:3.12-slim
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends ffmpeg curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 user
WORKDIR /app
RUN pip install --no-cache-dir kokoro-onnx soundfile fastapi "uvicorn[standard]"
RUN curl -sSL -o kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx \
 && curl -sSL -o voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
COPY app.py .
RUN chown -R user /app
USER user
EXPOSE 7860
# Render gives the port in $PORT; Hugging Face uses 7860.
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}"]
