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
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-gray-100 p-2 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-center items-center py-2">
          {links.map((link) => {
            const isActive = router.pathname === link.path;
            return (
              <Link legacyBehavior key={link.name} href={link.path}>
                <a
                  className={`mx-4 p-3 w-28 text-center rounded-lg text-black text-sm shadow-sm border-2 ${isActive ? "bg-green-300 border-white" : "bg-gray-300 border-gray-400"
                    } hover:bg-gray-200 transition-colors duration-300`}
                >
                  {link.name}
                </a>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
