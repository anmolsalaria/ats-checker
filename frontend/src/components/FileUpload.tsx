"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, X } from "lucide-react";

interface FileUploadProps {
  file: File | null;
  onFileSelect: (file: File | null) => void;
}

export default function FileUpload({ file, onFileSelect }: FileUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10 MB
  });

  if (file) {
    return (
      <div className="flex items-center justify-between rounded-lg border border-primary-200 bg-primary-50 p-4">
        <div className="flex items-center gap-3">
          <FileText className="h-8 w-8 text-primary-600" />
          <div>
            <p className="text-sm font-medium text-gray-900">{file.name}</p>
            <p className="text-xs text-gray-500">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>
        <button
          onClick={() => onFileSelect(null)}
          className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          aria-label="Remove file"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
        isDragActive
          ? "border-primary-400 bg-primary-50"
          : "border-gray-300 hover:border-primary-400 hover:bg-gray-50"
      }`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto mb-3 h-10 w-10 text-gray-400" />
      <p className="text-sm font-medium text-gray-700">
        {isDragActive
          ? "Drop your resume here..."
          : "Drag & drop your resume, or click to browse"}
      </p>
      <p className="mt-1 text-xs text-gray-500">PDF or DOCX — Max 10 MB</p>
    </div>
  );
}
