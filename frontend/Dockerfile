FROM node:20-alpine

WORKDIR /app

# install deps
COPY package.json package-lock.json* ./
RUN npm install

# copy app
COPY . .

# build time env
ENV NEXT_PUBLIC_API_URL=http://backend:8000

EXPOSE 3000

CMD ["npm", "run", "dev"]
