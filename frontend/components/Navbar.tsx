"use client";

import Link from "next/link";
import { useRouter } from "next/router";

const Navbar = () => {
  const router = useRouter();

  const links = [
    { name: "Search", path: "/" },
    { name: "Documents", path: "/document_explorer" },
    { name: "Status", path: "/status" },
  ];

  return (
    <nav className="fixed z-10 bottom-5 left-0 right-0 mx-auto animate-pop-in rounded-2xl overflow-hidden w-max transform transition-all duration-500 backdrop-filter backdrop-blur-sm p-4 hidden lg:flex">
      {links.map((link) => {
        const isActive = router.pathname === link.path;
        return (
          <Link legacyBehavior key={link.name} href={link.path}>
            <a
              className={`mx-12 text-zinc-700 font-thin text-opacity-50 hover:scale-110 transform transition-all duration-500 hover:text-yellow-400 hover:text-opacity-100 ${isActive ? "text-white" : ""
                }`}
            >
              {link.name}
            </a>
          </Link>
        );
      })}
    </nav>
  );
};

export default Navbar;
