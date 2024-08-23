import { FormattedDocument } from "@/app/types";
import { VerbaVector } from "@/app/types";
import * as THREE from "three";

export function splitDocument(
  fullText: string,
  searchSubstring: string | null
): FormattedDocument {
  if (searchSubstring === null || searchSubstring === "") {
    const beginning = fullText;
    const substring = "";
    const ending = "";

    return { beginning, substring, ending };
  }

  const startIndex = fullText.indexOf(searchSubstring);
  if (startIndex === -1) {
    // Substring not found, handle as appropriate, maybe return null or the full text as beginning
    return { beginning: fullText, substring: "", ending: "" };
  }

  const endIndex = startIndex + searchSubstring.length;

  const beginning = fullText.substring(0, startIndex);
  const substring = fullText.substring(startIndex, endIndex);
  const ending = fullText.substring(endIndex);

  return { beginning, substring, ending };
}

export const colors = [
  "green", // High contrast start
  "blue", // High contrast with red
  "red", // High contrast with green
  "yellow", // High contrast with blue
  "purple", // High contrast with yellow
  "cyan", // High contrast with purple
  "orange", // High contrast with cyan
  "limegreen", // High contrast with orange
  "pink", // High contrast with limegreen
  "teal", // High contrast with pink
  "violet", // High contrast with teal
  "forestgreen", // High contrast with violet
  "gold", // High contrast with forestgreen
  "navy", // High contrast with gold
  "magenta", // High contrast with navy
  "mediumspringgreen", // High contrast with magenta
  "darkorange", // High contrast with mediumspringgreen
  "deepskyblue", // High contrast with darkorange
  "crimson", // High contrast with deepskyblue
  "lightseagreen", // High contrast with crimson
  "royalblue", // High contrast with lightseagreen
  "chartreuse", // High contrast with royalblue
  "mediumorchid", // High contrast with chartreuse
  "aqua", // High contrast with mediumorchid
  "orangered", // High contrast with aqua
  "mediumaquamarine", // High contrast with orangered
  "plum", // High contrast with mediumaquamarine
  "lime", // High contrast with plum
  "dodgerblue", // High contrast with lime
  "lightcoral", // High contrast with dodgerblue
  "mediumslateblue", // High contrast with lightcoral
  "lightgreen", // High contrast with mediumslateblue
  "darkred", // High contrast with lightgreen
  "springgreen", // High contrast with darkred
  "lightpink", // High contrast with springgreen
  "indigo", // High contrast with lightpink
  "lightyellow", // High contrast with indigo
  "mediumvioletred", // High contrast with lightyellow
  "seagreen", // High contrast with mediumvioletred
  "fuchsia", // High contrast with seagreen
  "darkseagreen", // High contrast with fuchsia
  "thistle", // High contrast with darkseagreen
  "orange", // High contrast with thistle
  "powderblue", // High contrast with orange
  "yellowgreen", // High contrast with powderblue
  "cornflowerblue", // High contrast with yellowgreen
  "darkmagenta", // High contrast with cornflowerblue
  "darkblue", // High contrast with darkmagenta
  "gold", // High contrast with darkblue
  "mediumblue", // High contrast with gold
  "rosybrown", // High contrast with mediumblue
  "darkgreen", // High contrast with rosybrown
  "lightskyblue", // High contrast with darkgreen
  "mediumseagreen", // High contrast with lightskyblue
  "firebrick", // High contrast with mediumseagreen
  "lavender", // High contrast with firebrick
  "darkcyan", // High contrast with lavender
  "khaki", // High contrast with darkcyan
  "mediumturquoise", // High contrast with khaki
  "saddlebrown", // High contrast with mediumturquoise
  "lightblue", // High contrast with saddlebrown
  "olive", // High contrast with lightblue
  "mintcream", // High contrast with olive
  "turquoise", // High contrast with mintcream
  "rebeccapurple", // High contrast with turquoise
  "lightgoldenrodyellow", // High contrast with rebeccapurple
];

export function normalize(value: number, min: number, max: number): number {
  if (max === min) return 0; // Avoid division by zero
  return (value - min) / (max - min);
}

export function vectorToColor(
  vector: VerbaVector,
  minX: number,
  maxX: number,
  minY: number,
  maxY: number,
  minZ: number,
  maxZ: number
): THREE.Color {
  // Normalize vector components to be within the range of 0 to 1 based on min and max
  const normalizedX = normalize(vector.x, minX, maxX);
  const normalizedY = normalize(vector.y, minY, maxY);
  const normalizedZ = normalize(vector.z, minZ, maxZ);

  // Scale normalized values to 0-255
  const r = Math.floor(normalizedZ * 255); // Red from Z axis
  const g = Math.floor(normalizedX * 255); // Green from X axis
  const b = Math.floor(normalizedY * 255); // Blue from Y axis

  return new THREE.Color(`rgb(${g},${b},${r})`);
}
