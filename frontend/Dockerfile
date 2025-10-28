FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "run", "dev", "--", "--host"]
