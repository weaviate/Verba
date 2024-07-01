# Verba - Frontend Documentation

Verba's Frontend is a [NextJS](https://nextjs.org/) application used together with [TailwindCSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/).

## 🚀 Setting Up the Frontend

To get your local copy of the Verba frontend up and running, please follow these simple steps:

1. Clone Repository

```git

git clone https://github.com/weaviate/Verba.git

```

1. **Node.js Requirement**:

   - Confirm that Node.js version `>=21.3.0` is installed on your system. If you need to install or update Node.js, visit the official [Node.js website](https://nodejs.org/).

2. **Installation**:

   - Navigate to the frontend directory: `cd frontend`
   - Run `npm install` to install the dependencies required for the project.

3. **Development Server**:
   - Launch the application in development mode by executing `npm run dev`.
   - Open your web browser and visit `http://localhost:3000` to view the application.

## 📦 Building Static Pages for FastAPI

If you wish to serve and update the frontend through FastAPI, you need to build static pages:

1. **Build Process**:
   - Execute `npm run build` to generate the static production build. The output will be directed to the FastAPI folder configured to serve the static content.
