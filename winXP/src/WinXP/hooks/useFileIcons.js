import { useState, useEffect } from 'react';
import fileService from '../../services/fileService';

/**
 * Hook to manage dynamic file icons from downloads folder
 */
export function useFileIcons() {
  const [fileIcons, setFileIcons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchFiles = async () => {
      try {
        setLoading(true);
        const files = await fileService.getFiles();
        
        if (!isMounted) return;

        // Convert files to icon format
        const icons = files.map((file, index) => ({
          id: 1000 + index, // Start from 1000 to avoid conflicts with static icons
          icon: fileService.getFileIcon(file),
          title: file.name,
          component: fileService.getAppForFile(file),
          isFocus: false,
          fileData: file, // Store original file data
          isFile: true, // Mark as dynamic file
        }));

        setFileIcons(icons);
        setError(null);
      } catch (err) {
        if (isMounted) {
          setError(err.message);
          console.error('Error fetching file icons:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    // Only fetch once on component mount
    fetchFiles();

    return () => {
      isMounted = false;
    };
  }, []);

  return { fileIcons, loading, error, refetch: () => setLoading(true) };
}

export default useFileIcons;