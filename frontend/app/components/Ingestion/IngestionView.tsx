"use client";

import React, { useState, useEffect } from "react";
import FileSelectionView from "./FileSelectionView";
import ConfigurationView from "./ConfigurationView";
import {
  FileMap,
  StatusReport,
  CreateNewDocument,
  FileData,
  Credentials,
} from "@/app/types";
import { RAGConfig } from "@/app/types";
import { getImportWebSocketApiHost } from "@/app/util";

interface IngestionViewProps {
  credentials: Credentials;
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  addStatusMessage: (
    message: string,
    type: "INFO" | "WARNING" | "SUCCESS" | "ERROR"
  ) => void;
}

const IngestionView: React.FC<IngestionViewProps> = ({
  credentials,
  RAGConfig,
  setRAGConfig,
  addStatusMessage,
}) => {
  const [fileMap, setFileMap] = useState<FileMap>({});
  const [selectedFileData, setSelectedFileData] = useState<string | null>(null);
  const [reconnect, setReconnect] = useState(false);
  const [socket, setSocket] = useState<WebSocket | null>(null);

  const [socketStatus, setSocketStatus] = useState<"ONLINE" | "OFFLINE">(
    "OFFLINE"
  );

  useEffect(() => {
    setReconnect(true);
  }, []);

  // Setup Import WebSocket and messages
  useEffect(() => {
    const socketHost = getImportWebSocketApiHost();
    const localSocket = new WebSocket(socketHost);

    localSocket.onopen = () => {
      console.log("Import WebSocket connection opened to " + socketHost);
      setSocketStatus("ONLINE");
    };

    localSocket.onmessage = (event) => {
      setSocketStatus("ONLINE");
      try {
        const data: StatusReport | CreateNewDocument = JSON.parse(event.data);
        if ("new_file_id" in data) {
          setFileMap((prevFileMap) => {
            const newFileMap: FileMap = { ...prevFileMap };
            newFileMap[data.new_file_id] = {
              ...newFileMap[data.original_file_id],
              fileID: data.new_file_id,
              filename: data.filename,
              block: true,
            };
            return newFileMap;
          });
        } else {
          updateStatus(data);
        }
      } catch (e) {
        console.error("Received data is not valid JSON:", event.data);
        return;
      }
    };

    localSocket.onerror = (error) => {
      console.error("Import WebSocket Error:", error);
      setSocketStatus("OFFLINE");
      setSocketErrorStatus();
      setReconnect((prev) => !prev);
    };

    localSocket.onclose = (event) => {
      setSocketStatus("OFFLINE");
      setSocketErrorStatus();
      if (event.wasClean) {
        console.log(
          `Import WebSocket connection closed cleanly, code=${event.code}, reason=${event.reason}`
        );
      } else {
        console.error("WebSocket connection died");
      }
      setReconnect((prev) => !prev);
    };

    setSocket(localSocket);

    return () => {
      if (localSocket.readyState !== WebSocket.CLOSED) {
        localSocket.close();
      }
    };
  }, [reconnect]);

  const reconnectToVerba = () => {
    setReconnect((prevState) => !prevState);
  };

  const setSocketErrorStatus = () => {
    setFileMap((prevFileMap) => {
      if (fileMap) {
        const newFileMap = { ...prevFileMap };
        for (const fileMapKey in newFileMap) {
          if (
            newFileMap[fileMapKey].status != "DONE" &&
            newFileMap[fileMapKey].status != "ERROR" &&
            newFileMap[fileMapKey].status != "READY"
          ) {
            newFileMap[fileMapKey].status = "ERROR";
            newFileMap[fileMapKey].status_report["ERROR"] = {
              fileID: fileMapKey,
              status: "ERROR",
              message: "Connection was interrupted",
              took: 0,
            };
          }
        }
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  const updateStatus = (data: StatusReport) => {
    console.log("Update status", data);
    if (data.status === "DONE") {
      addStatusMessage("File " + data.fileID + " imported", "SUCCESS");
    }
    if (data.status === "ERROR") {
      addStatusMessage("File " + data.fileID + " import failed", "ERROR");
    }
    setFileMap((prevFileMap) => {
      if (data && data.fileID in prevFileMap) {
        const newFileData: FileData = JSON.parse(
          JSON.stringify(prevFileMap[data.fileID])
        );
        const newFileMap: FileMap = { ...prevFileMap };
        newFileData.status = data.status;
        newFileData.status_report[data.status] = data;
        newFileMap[data.fileID] = newFileData;
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  const setInitialStatus = (fileID: string) => {
    setFileMap((prevFileMap) => {
      if (fileID in prevFileMap) {
        const newFileData: FileData = JSON.parse(
          JSON.stringify(prevFileMap[fileID])
        );
        const newFileMap: FileMap = { ...prevFileMap };
        newFileData.status = "WAITING";
        if (Object.entries(newFileData.status_report).length > 0) {
          newFileData.status_report = {};
        }
        newFileMap[fileID] = newFileData;
        return newFileMap;
      }
      return prevFileMap;
    });
  };

  const importSelected = () => {
    addStatusMessage("Importing selected file", "INFO");
    if (
      selectedFileData &&
      ["READY", "DONE", "ERROR"].includes(fileMap[selectedFileData].status) &&
      !fileMap[selectedFileData].block
    ) {
      sendDataBatches(
        JSON.stringify(fileMap[selectedFileData]),
        selectedFileData
      );
    }
  };

  const importAll = () => {
    addStatusMessage("Importing all files", "INFO");
    for (const fileID in fileMap) {
      if (
        ["READY", "DONE", "ERROR"].includes(fileMap[fileID].status) &&
        !fileMap[fileID].block
      ) {
        sendDataBatches(JSON.stringify(fileMap[fileID]), fileID);
      }
    }
  };

  const sendDataBatches = (data: string, fileID: string) => {
    if (socket?.readyState === WebSocket.OPEN) {
      setInitialStatus(fileID);
      const chunkSize = 2000; // Define chunk size (in bytes)
      const batches = [];
      let offset = 0;

      // Create the batches
      while (offset < data.length) {
        const chunk = data.slice(offset, offset + chunkSize);
        batches.push(chunk);
        offset += chunkSize;
      }

      const totalBatches = batches.length;

      // Send the batches
      batches.forEach((chunk, order) => {
        socket.send(
          JSON.stringify({
            chunk: chunk,
            isLastChunk: order === totalBatches - 1,
            total: totalBatches,
            order: order,
            fileID: fileID,
            credentials: credentials,
          })
        );
      });
    } else {
      console.error("WebSocket is not open. ReadyState:", socket?.readyState);
      setReconnect((prevState) => !prevState);
    }
  };

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div
        className={`${selectedFileData ? "hidden md:flex md:w-[45vw]" : "w-full md:w-[45vw] md:flex"}`}
      >
        <FileSelectionView
          fileMap={fileMap}
          addStatusMessage={addStatusMessage}
          setFileMap={setFileMap}
          RAGConfig={RAGConfig}
          setRAGConfig={setRAGConfig}
          selectedFileData={selectedFileData}
          setSelectedFileData={setSelectedFileData}
          importSelected={importSelected}
          importAll={importAll}
          socketStatus={socketStatus}
          reconnect={reconnectToVerba}
        />
      </div>

      <div
        className={`${selectedFileData ? "md:w-[55vw] w-full flex" : "hidden md:flex md:w-[55vw]"}`}
      >
        {selectedFileData && (
          <ConfigurationView
            addStatusMessage={addStatusMessage}
            selectedFileData={selectedFileData}
            RAGConfig={RAGConfig}
            credentials={credentials}
            setRAGConfig={setRAGConfig}
            fileMap={fileMap}
            setFileMap={setFileMap}
            setSelectedFileData={setSelectedFileData}
          />
        )}
      </div>
    </div>
  );
};

export default IngestionView;
