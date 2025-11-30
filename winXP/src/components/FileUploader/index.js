import React, { useState } from 'react';
import styled from 'styled-components';
import API_URL from '../../config';

const FileUploader = ({ onClose, onUploadComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Please select a file first');
      return;
    }

    setUploading(true);
    setMessage('Uploading...');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch(`${API_URL}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setMessage(`✓ ${selectedFile.name} uploaded and processed!`);
        setSelectedFile(null);
        if (onUploadComplete) {
          onUploadComplete(data);
        }
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        setMessage(`✗ Upload failed: ${data.error}`);
      }
    } catch (error) {
      setMessage(`✗ Upload error: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
      setMessage('');
    }
  };

  return (
    <Window>
      <TitleBar>
        <TitleText>Upload File to Knowledge Base</TitleText>
        <CloseButton onClick={onClose}>×</CloseButton>
      </TitleBar>
      
      <Content>
        <DropZone
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <DropText>
            {selectedFile ? (
              <>
                <FileIcon>📄</FileIcon>
                <FileName>{selectedFile.name}</FileName>
                <FileSize>{(selectedFile.size / 1024).toFixed(2)} KB</FileSize>
              </>
            ) : (
              <>
                <UploadIcon>📤</UploadIcon>
                <DropText>Drop file here or click to browse</DropText>
                <SupportedFormats>
                  Supports: PDF, TXT, MD, PNG, JPG, JPEG
                </SupportedFormats>
              </>
            )}
          </DropZone>

          <input
            id="fileInput"
            type="file"
            accept=".pdf,.txt,.md,.png,.jpg,.jpeg"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          {message && (
            <Message success={message.startsWith('✓')}>
              {message}
            </Message>
          )}

          <ButtonGroup>
            <UploadButton 
              onClick={handleUpload} 
              disabled={!selectedFile || uploading}
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </UploadButton>
            <CancelButton onClick={onClose}>Cancel</CancelButton>
          </ButtonGroup>
        </Content>
    </Window>
  );
};

const Window = styled.div`
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  background: #ece9d8;
  border: 2px solid #0054e3;
  box-shadow: 4px 4px 10px rgba(0, 0, 0, 0.3);
  z-index: 10000;
`;

const TitleBar = styled.div`
  background: linear-gradient(to right, #0054e3, #3c8dda);
  color: white;
  padding: 4px 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 13px;
`;

const TitleText = styled.span`
  font-family: 'Tahoma', sans-serif;
`;

const CloseButton = styled.button`
  background: #c0504d;
  border: 1px solid #fff;
  color: white;
  font-size: 16px;
  width: 22px;
  height: 20px;
  cursor: pointer;
  font-weight: bold;
  padding: 0;

  &:hover {
    background: #e74c3c;
  }

  &:active {
    background: #a94442;
  }
`;

const Content = styled.div`
  padding: 20px;
`;

const DropZone = styled.div`
  border: 2px dashed #0054e3;
  border-radius: 4px;
  padding: 40px;
  text-align: center;
  background: white;
  cursor: pointer;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &:hover {
    background: #f0f8ff;
    border-color: #3c8dda;
  }
`;

const UploadIcon = styled.div`
  font-size: 48px;
  margin-bottom: 10px;
`;

const FileIcon = styled.div`
  font-size: 48px;
  margin-bottom: 10px;
`;

const FileName = styled.div`
  font-weight: bold;
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
`;

const FileSize = styled.div`
  font-size: 12px;
  color: #666;
`;

const DropText = styled.p`
  color: #0054e3;
  font-weight: bold;
  margin: 10px 0;
  font-size: 14px;
`;

const SupportedFormats = styled.p`
  color: #666;
  font-size: 12px;
  margin-top: 10px;
`;

const Message = styled.div`
  margin: 15px 0;
  padding: 10px;
  border-radius: 4px;
  background: ${props => props.success ? '#d4edda' : '#f8d7da'};
  color: ${props => props.success ? '#155724' : '#721c24'};
  border: 1px solid ${props => props.success ? '#c3e6cb' : '#f5c6cb'};
  font-size: 13px;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
`;

const UploadButton = styled.button`
  flex: 1;
  padding: 8px 16px;
  background: #0054e3;
  color: white;
  border: 1px solid #003ea3;
  border-radius: 3px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;

  &:hover:not(:disabled) {
    background: #3c8dda;
  }

  &:active:not(:disabled) {
    background: #003ea3;
  }

  &:disabled {
    background: #ccc;
    cursor: not-allowed;
    border-color: #999;
  }
`;

const CancelButton = styled.button`
  flex: 1;
  padding: 8px 16px;
  background: #d3d3d3;
  color: #333;
  border: 1px solid #999;
  border-radius: 3px;
  cursor: pointer;
  font-size: 13px;
  font-weight: bold;

  &:hover {
    background: #c0c0c0;
  }

  &:active {
    background: #a0a0a0;
  }
`;

export default FileUploader;
