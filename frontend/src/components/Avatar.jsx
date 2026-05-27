import { useMemo } from "react";
import { createAvatar } from "@dicebear/core";
import {
  adventurer,
  avataaars,
  lorelei,
  micah,
  notionists,
  personas,
} from "@dicebear/collection";

const STYLES = { adventurer, avataaars, lorelei, micah, notionists, personas };

// Renders a deterministic generated portrait from the employee's avatar config.
export default function Avatar({ avatar = {}, size = 74 }) {
  const uri = useMemo(() => {
    const collection = STYLES[avatar.style] || notionists;
    const bg = (avatar.color || "#4f46e5").replace("#", "");
    return createAvatar(collection, {
      seed: avatar.seed || "employee",
      size,
      radius: 50,
      backgroundColor: [bg],
    }).toDataUri();
  }, [avatar.style, avatar.seed, avatar.color, size]);

  return (
    <img
      src={uri}
      width={size}
      height={size}
      alt="avatar"
      style={{ borderRadius: "50%", display: "block" }}
    />
  );
}
