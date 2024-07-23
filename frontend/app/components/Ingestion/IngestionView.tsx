"use client";

import React, { useState, useEffect, use } from "react";

import FileSelectionView from "./FileSelectionView";
import ConfigurationView from "./ConfigurationView";
import { SettingsConfiguration } from "../Settings/types";

import { FileMap, StatusReport } from "./types";
import { RAGConfig } from "../RAG/types";

import { getImportWebSocketApiHost } from "../RAG/util";

import { FileData } from "./types";

interface IngestionViewProps {
  settingConfig: SettingsConfiguration;
  RAGConfig: RAGConfig | null;
  setRAGConfig: React.Dispatch<React.SetStateAction<RAGConfig | null>>;
  setReconnectMain: React.Dispatch<React.SetStateAction<boolean>>;
  APIHost: string | null;
}

const IngestionView: React.FC<IngestionViewProps> = ({
  settingConfig,
  RAGConfig,
  setRAGConfig,
  setReconnectMain,
  APIHost,
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
        const data: StatusReport = JSON.parse(event.data);
        updateStatus(data);
      } catch (e) {
        console.error("Received data is not valid JSON:", event.data);
        return;
      }
    };

    localSocket.onerror = (error) => {
      console.error("Import WebSocket Error:", error);
      setSocketStatus("OFFLINE");
      setSocketErrorStatus();
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
    setReconnectMain((prevState) => !prevState);
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
    if (
      selectedFileData &&
      ["READY", "DONE", "ERROR"].includes(fileMap[selectedFileData].status)
    ) {
      if (socket?.readyState === WebSocket.OPEN) {
        setInitialStatus(selectedFileData);
        socket.send(JSON.stringify(fileMap[selectedFileData]));
      } else {
        console.error("WebSocket is not open. ReadyState:", socket?.readyState);
        setReconnect((prevState) => !prevState);
      }
    }
  };

  const importAll = () => {
    for (const fileID in fileMap) {
      if (["READY", "DONE", "ERROR"].includes(fileMap[fileID].status)) {
        if (socket?.readyState === WebSocket.OPEN) {
          setInitialStatus(fileID);
          socket.send(JSON.stringify(fileMap[fileID]));
        } else {
          console.error(
            "WebSocket is not open. ReadyState:",
            socket?.readyState
          );
          setReconnect((prevState) => !prevState);
        }
      }
    }
  };

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div
        className={`${selectedFileData ? "hidden lg:flex lg:w-[45vw]" : "w-full lg:w-[45vw] lg:flex"}`}
      >
        <FileSelectionView
          settingConfig={settingConfig}
          fileMap={fileMap}
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
        className={`${selectedFileData ? "lg:w-[55vw] w-full flex" : "hidden lg:flex lg:w-[55vw]"}`}
      >
        {selectedFileData && (
          <ConfigurationView
            settingConfig={settingConfig}
            selectedFileData={selectedFileData}
            RAGConfig={RAGConfig}
            APIHost={APIHost}
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