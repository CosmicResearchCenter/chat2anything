# Stage 1: Build the project
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --registry https://registry.npmmirror.com
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
