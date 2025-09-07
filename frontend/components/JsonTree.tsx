"use client";

import "react-json-view-lite/dist/index.css";
import { JsonView, defaultStyles } from "react-json-view-lite";

function annotateArrayIndexes(value: any): any {
  // Recursively convert arrays to index-keyed objects for display
  if (Array.isArray(value)) {
    const obj: Record<string, any> = {};
    for (let i = 0; i < value.length; i++) {
      obj[i] = annotateArrayIndexes(value[i]);
    }
    return obj;
  }
  if (value && typeof value === "object") {
    const out: Record<string, any> = {};
    for (const [k, v] of Object.entries(value)) {
      out[k] = annotateArrayIndexes(v);
    }
    return out;
  }
  return value;
}

export default function JsonTree({
  data,
  showArrayIndexes = true,
}: {
  data: any;
  showArrayIndexes?: boolean;
}) {
  const displayData = showArrayIndexes ? annotateArrayIndexes(data) : data;
  return (
    <div className="overflow-auto">
      <JsonView
        data={displayData}
        shouldExpandNodeInitially={({ level }) => level < 1} // collapsed like Streamlit
        style={defaultStyles}
      />
    </div>
  );
}
