/**
 * Service to interact with the file server backend
 */

import notepadIcon from 'assets/windowsIcons/327(32x32).png';
import API_URL from '../config';

const API_BASE_URL = API_URL;

// Online icon sources
const ONLINE_ICONS = {
  text: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_text.svg',
  pdf: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_pdf2.svg',
  image: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_image.svg',
  video: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_video.svg',
  audio: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_audio.svg',
  document: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_word.svg',
  spreadsheet: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_excel.svg',
  archive: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_zip.svg',
  code: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/file_type_js.svg',
  unknown: 'https://raw.githubusercontent.com/microsoft/vscode-icons/main/icons/default_file.svg'
};

export const fileService = {
  /**
   * Fetch list of files from downloads folder
   * @returns {Promise<Array>} Array of file objects
   */
  async getFiles() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/files`, {
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching files:', error);
      return [];
    }
  },

  /**
   * Get the download URL for a file
   * @param {string} filename - Name of the file
   * @returns {string} Download URL
   */
  getDownloadUrl(filename) {
    return `${API_BASE_URL}/api/download/${encodeURIComponent(filename)}`;
  },

  /**
   * Get appropriate icon for file type
   * @param {Object} file - File object with type and name
   * @returns {string} Icon path
   */
  getFileIcon(file) {
    // Use notepad icon for text files (keeping local asset as requested)
    if (file.type === 'text') {
      return notepadIcon;
    }
    
    // Use icon URL provided by backend if available
    if (file.icon) {
      return file.icon;
    }
    
    // Fallback to online icons
    return ONLINE_ICONS[file.type] || ONLINE_ICONS.unknown;
  },

  /**
   * Get appropriate app component for file type
   * @param {Object} file - File object
   * @returns {string} App component name
   */
  getAppForFile(file) {
    switch (file.type) {
      case 'text':
      case 'code':
        return 'Notepad';
      case 'pdf':
        return 'PDFViewer';
      case 'image':
        return 'ImageViewer';
      case 'document':
      case 'spreadsheet':
      case 'archive':
        return 'Notepad'; // Default to notepad for these
      default:
        return 'Notepad'; // Default to notepad for unknown files
    }
  },

  /**
   * Create window title for file
   * @param {Object} file - File object
   * @returns {string} Window title
   */
  getWindowTitle(file) {
    switch (file.type) {
      case 'text':
      case 'code':
        return `${file.name} - Notepad`;
      case 'pdf':
        return `${file.name} - PDF Viewer`;
      case 'image':
        return `${file.name} - Image Viewer`;
      case 'document':
        return `${file.name} - Document Viewer`;
      case 'spreadsheet':
        return `${file.name} - Spreadsheet Viewer`;
      case 'archive':
        return `${file.name} - Archive`;
      default:
        return `${file.name} - Notepad`;
    }
  }
};

export default fileService;