# picking some random python image
FROM python:3.10-slim

# defining my working directory inside the container
WORKDIR /app

# there's only one third party package (to display colors)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy the entire app
COPY . /app/

# make it executable
RUN chmod +x /app/zyra.py

RUN ln -s /app/zyra.py /usr/local/bin/zyra

EXPOSE 8080

CMD ["/bin/bash"]