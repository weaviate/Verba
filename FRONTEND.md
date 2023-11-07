# 🎨 Verba - Frontend Documentation 🎨

Welcome to the Verba frontend documentation. Our frontend is a React application utilizing the robust Next.js framework, designed to offer a dynamic and interactive document search and display experience. Below are the instructions to help you set up and understand the structure of the frontend, which can be found within the [frontend](./frontend/) directory of our repository.

## 🚀 Setting Up the Frontend

To get your local copy of the Verba frontend up and running, please follow these simple steps:

1. **Node.js Requirement**:
   - Confirm that Node.js version `>=18.16.0` is installed on your system. If you need to install or update Node.js, visit the official [Node.js website](https://nodejs.org/).

2. **Installation**:
   - Navigate to the frontend directory: `cd frontend`
   - Run `npm install` to install the dependencies required for the project.

3. **Development Server**:
   - Launch the application in development mode by executing `npm run dev`.
   - Open your web browser and visit `http://localhost:3000` to view the application.

## 📦 Building Static Pages for FastAPI

If you wish to serve the frontend through FastAPI, you need to build static pages:

1. **Build Process**:
   - Execute `npm run build` to generate the static production build. The output will be directed to the FastAPI folder configured to serve the static content.

## 🎨 Styling with Tailwind CSS

Verba's frontend is styled with Tailwind CSS, a utility-first CSS framework, along with global CSS classes for a consistent and modern design language. Here's how styling is managed:

- **Tailwind CSS**:
  - We use Tailwind CSS for responsive design and to apply styles directly in the JSX code using utility classes.
  - For custom styling, the `tailwind.config.js` file can be modified.

- **Global Styles**:
  - Global stylesheets are located in the `styles` directory. These are used for overarching styles that apply to the entire application.

- **Assets**:
  - All static assets such as images and animations are housed in the `public` directory.
  - These assets are referenced directly in the codebase and are automatically optimized by Next.js.

By following these guidelines, you'll be able to contribute to the frontend of Verba effectively. We value your contributions and are excited to see the creative ways you'll enhance the Verba experience.

