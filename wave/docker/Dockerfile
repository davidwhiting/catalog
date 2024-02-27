# FROM python:3.9
# When running on M1 Mac, use the following --platform option.
FROM --platform=linux/amd64 python:3.9

WORKDIR /code

COPY . .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Change the port number of our Wave app to 7860
# which is default in Hugging Face Spaces.
ENV H2O_WAVE_LISTEN=":7860"
ENV H2O_WAVE_ADDRESS='http://127.0.0.1:7860'

CMD ["wave", "run", "app", "--no-reload"]
