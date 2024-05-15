import { FileData } from "./types";

export function arrayBufferToBase64(buffer: ArrayBuffer): string {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary); // Encode the binary string to base64
}

export function processFiles(fileList: FileList): Promise<FileData[]> {
  return Promise.all(
    Array.from(fileList).map(
      (file) =>
        new Promise<FileData>((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => {
            const arrayBuffer = reader.result as ArrayBuffer;
            const content = arrayBufferToBase64(arrayBuffer);
            const filename = file.name;
            const extension = file.name.split(".").pop() || "";
            resolve({
              filename,
              extension,
              content,
            });
          };
          reader.onerror = () => reject(reader.error);

          reader.readAsArrayBuffer(file);
        })
    )
  );
}
