"use client";

import React, { useState, useEffect, use } from "react";

import FileSelectionView from "./FileSelectionView";
import ConfigurationView from "./ConfigurationView";
import { SettingsConfiguration } from "../Settings/types";

import { FileMap } from "./types";
import { RAGConfig } from "../RAG/types";

import { getImportWebSocketApiHost } from "../RAG/util";

import { FileData } from "./types";

interface IngestionViewProps {
  settingConfig: SettingsConfiguration;
  RAGConfig: RAGConfig | null;
  setRAGConfig: (r_: RAGConfig | null) => void;
}

const IngestionView: React.FC<IngestionViewProps> = ({
  settingConfig,
  RAGConfig,
  setRAGConfig,
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
      let data;
      setSocketStatus("ONLINE");

      try {
        data = JSON.parse(event.data);
        console.log(data);
      } catch (e) {
        console.error("Received data is not valid JSON:", event.data);
        return;
      }
    };

    localSocket.onerror = (error) => {
      console.error("Import WebSocket Error:", error);
      setSocketStatus("OFFLINE");
    };

    localSocket.onclose = (event) => {
      setSocketStatus("OFFLINE");
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
  };

  const importSelected = () => {
    if (selectedFileData) {
      if (socket?.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(fileMap[selectedFileData]));
      } else {
        console.error("WebSocket is not open. ReadyState:", socket?.readyState);
        setReconnect((prevState) => !prevState);
      }
    }
  };

  return (
    <div className="flex justify-center gap-3 h-[80vh] ">
      <div className="flex w-1/2">
        <FileSelectionView
          settingConfig={settingConfig}
          fileMap={fileMap}
          setFileMap={setFileMap}
          RAGConfig={RAGConfig}
          setRAGConfig={setRAGConfig}
          selectedFileData={selectedFileData}
          setSelectedFileData={setSelectedFileData}
          importSelected={importSelected}
          socketStatus={socketStatus}
          reconnect={reconnectToVerba}
        />
      </div>

      <div className="flex w-1/2">
        {selectedFileData && socketStatus === "ONLINE" && (
          <ConfigurationView
            settingConfig={settingConfig}
            selectedFileData={selectedFileData}
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
