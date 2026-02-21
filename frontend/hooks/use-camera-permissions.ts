import { useCameraPermissions as useExpoCamera } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library';
import { useState } from 'react';

export interface PermissionStatus {
  camera: boolean;
  photoLibrary: boolean;
  isLoading: boolean;
  error: string | null;
}

/**
 * Hook to manage camera and photo library permissions
 * Handles requesting permissions with user-friendly error messages
 */
export const useCameraPermissions = () => {
  const [cameraPermission, requestCameraPermission] = useExpoCamera();
  const [mediaLibraryPermission, requestMediaLibraryPermission] =
    MediaLibrary.usePermissions();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requestPermissions = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Request camera permission
      if (!cameraPermission?.granted) {
        const cameraResult = await requestCameraPermission();
        if (!cameraResult.granted) {
          setError(
            'Camera permission is required to take photos. Please enable it in settings.'
          );
          setIsLoading(false);
          return false;
        }
      }

      // Request photo library permission
      if (!mediaLibraryPermission?.granted) {
        const libraryResult = await requestMediaLibraryPermission();
        if (!libraryResult.granted) {
          setError(
            'Photo library permission is required to save photos. Please enable it in settings.'
          );
          setIsLoading(false);
          return false;
        }
      }

      setIsLoading(false);
      return true;
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'An error occurred while requesting permissions';
      setError(errorMessage);
      setIsLoading(false);
      return false;
    }
  };

  const status: PermissionStatus = {
    camera: cameraPermission?.granted ?? false,
    photoLibrary: mediaLibraryPermission?.granted ?? false,
    isLoading,
    error,
  };

  return { ...status, requestPermissions };
};
