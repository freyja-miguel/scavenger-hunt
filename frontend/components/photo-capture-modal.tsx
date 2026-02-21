import { useThemeColor } from '@/hooks/use-theme-color';
import { Ionicons } from '@expo/vector-icons';
import { CameraView, useCameraPermissions } from 'expo-camera';
import React, { useEffect, useRef, useState } from 'react';
import { ActivityIndicator, Alert, Modal, Pressable, View } from 'react-native';
import { ThemedText } from './themed-text';
import { ThemedView } from './themed-view';

export interface PhotoCaptureModalProps {
  visible: boolean;
  onPhotoCaptured: (photoUri: string) => void;
  onCancel: () => void;
  itemName: string; // Name of the item to capture (e.g., "shells")
}

/**
 * PhotoCaptureModal Component
 * Allows users to capture photos using device camera
 * Designed with child-friendly UX (large touch targets, clear feedback)
 */
export const PhotoCaptureModal: React.FC<PhotoCaptureModalProps> = ({
  visible,
  onPhotoCaptured,
  onCancel,
  itemName,
}) => {
  const [permission, requestPermission] = useCameraPermissions();
  const [cameraActive, setCameraActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const cameraRef = useRef(null);

  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');
  const primaryColor = useThemeColor({}, 'tint');

  // Request camera permission when modal opens
  useEffect(() => {
    if (visible && !permission?.granted) {
      requestPermission();
    }
  }, [visible, permission?.granted, requestPermission]);

  const handleTakePhoto = async () => {
    if (!cameraRef.current) return;

    try {
      setIsLoading(true);
      const photo = await (cameraRef.current as any).takePictureAsync({
        quality: 0.9,
        exif: true,
      });

      if (photo?.uri) {
        setCameraActive(false);
        onPhotoCaptured(photo.uri);
      }
    } catch (error) {
      Alert.alert(
        'Photo Error',
        'Failed to capture photo. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setCameraActive(false);
    onCancel();
  };

  // Permission denied screen
  if (visible && !permission?.granted) {
    return (
      <Modal
        visible={visible}
        transparent={true}
        animationType="slide"
        onRequestClose={handleCancel}
      >
        <ThemedView
          style={{
            flex: 1,
            justifyContent: 'center',
            alignItems: 'center',
            paddingHorizontal: 20,
          }}
        >
          <Ionicons
            name="lock-closed"
            size={64}
            color={textColor}
            style={{ marginBottom: 20 }}
          />
          <ThemedText style={{ fontSize: 18, marginBottom: 10, textAlign: 'center' }}>
            Camera Permission Required
          </ThemedText>
          <ThemedText style={{ textAlign: 'center', marginBottom: 30, opacity: 0.7 }}>
            We need access to your camera to capture photos of {itemName}.
          </ThemedText>

          <Pressable
            onPress={() => requestPermission()}
            style={({ pressed }) => ({
              backgroundColor: primaryColor,
              paddingVertical: 16,
              paddingHorizontal: 32,
              borderRadius: 8,
              marginBottom: 10,
              opacity: pressed ? 0.7 : 1,
            })}
          >
            <ThemedText style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>
              Grant Permission
            </ThemedText>
          </Pressable>

          <Pressable
            onPress={handleCancel}
            style={({ pressed }) => ({
              paddingVertical: 16,
              paddingHorizontal: 32,
              opacity: pressed ? 0.7 : 1,
            })}
          >
            <ThemedText style={{ fontSize: 16, color: primaryColor }}>Cancel</ThemedText>
          </Pressable>
        </ThemedView>
      </Modal>
    );
  }

  // Camera active screen
  if (visible && cameraActive && permission?.granted) {
    return (
      <Modal
        visible={visible && cameraActive}
        transparent={true}
        animationType="none"
        onRequestClose={handleCancel}
      >
        <View style={{ flex: 1, backgroundColor: '#000' }}>
          <CameraView
            ref={cameraRef}
            style={{ flex: 1 }}
            facing="back"
            autofocus="on"
          >
            {/* Top header */}
            <View
              style={{
                flexDirection: 'row',
                justifyContent: 'space-between',
                alignItems: 'center',
                paddingTop: 50,
                paddingHorizontal: 20,
                paddingBottom: 20,
              }}
            >
              <ThemedText style={{ color: '#fff', fontSize: 18, fontWeight: 'bold' }}>
                Capture {itemName}
              </ThemedText>
              <Pressable
                onPress={() => setCameraActive(false)}
                style={({ pressed }) => ({
                  opacity: pressed ? 0.7 : 1,
                })}
              >
                <Ionicons name="close" size={28} color="#fff" />
              </Pressable>
            </View>

            {/* Bottom controls */}
            <View
              style={{
                position: 'absolute',
                bottom: 40,
                left: 0,
                right: 0,
                flexDirection: 'row',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 20,
              }}
            >
              <Pressable
                onPress={() => setCameraActive(false)}
                disabled={isLoading}
                style={({ pressed }) => ({
                  width: 60,
                  height: 60,
                  borderRadius: 30,
                  backgroundColor: '#ff6b6b',
                  justifyContent: 'center',
                  alignItems: 'center',
                  opacity: pressed ? 0.7 : isLoading ? 0.5 : 1,
                })}
              >
                <Ionicons name="arrow-back" size={24} color="#fff" />
              </Pressable>

              <Pressable
                onPress={handleTakePhoto}
                disabled={isLoading}
                style={({ pressed }) => ({
                  width: 80,
                  height: 80,
                  borderRadius: 40,
                  backgroundColor: '#fff',
                  justifyContent: 'center',
                  alignItems: 'center',
                  borderWidth: 4,
                  borderColor: primaryColor,
                  opacity: pressed ? 0.7 : isLoading ? 0.5 : 1,
                })}
              >
                {isLoading ? (
                  <ActivityIndicator size="large" color={primaryColor} />
                ) : (
                  <View
                    style={{
                      width: 60,
                      height: 60,
                      borderRadius: 30,
                      backgroundColor: primaryColor,
                    }}
                  />
                )}
              </Pressable>

            </View>
          </CameraView>
        </View>
      </Modal>
    );
  }

  // Initial choice screen
  return (
    <Modal
      visible={visible && !cameraActive}
      transparent={true}
      animationType="slide"
      onRequestClose={handleCancel}
    >
      <ThemedView
        style={{
          flex: 1,
          justifyContent: 'center',
          alignItems: 'center',
          paddingHorizontal: 20,
        }}
      >
        <Ionicons
          name="camera"
          size={80}
          color={primaryColor}
          style={{ marginBottom: 30 }}
        />

        <ThemedText style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 10 }}>
          Capture {itemName}
        </ThemedText>

        <ThemedText
          style={{
            textAlign: 'center',
            marginBottom: 40,
            opacity: 0.7,
            fontSize: 16,
          }}
        >
          Take a live photo to find {itemName}
        </ThemedText>

        <Pressable
          onPress={() => setCameraActive(true)}
          disabled={isLoading}
          style={({ pressed }) => ({
            width: '100%',
            backgroundColor: primaryColor,
            paddingVertical: 18,
            borderRadius: 12,
            marginBottom: 20,
            opacity: pressed ? 0.7 : isLoading ? 0.5 : 1,
            flexDirection: 'row',
            justifyContent: 'center',
            alignItems: 'center',
            gap: 10,
          })}
        >
          <Ionicons name="camera" size={20} color="#fff" />
          <ThemedText style={{ color: '#fff', fontSize: 16, fontWeight: 'bold' }}>
            Take Photo
          </ThemedText>
        </Pressable>

        <Pressable
          onPress={handleCancel}
          disabled={isLoading}
          style={({ pressed }) => ({
            opacity: pressed ? 0.7 : isLoading ? 0.5 : 1,
            paddingVertical: 12,
          })}
        >
          <ThemedText style={{ fontSize: 16, color: textColor, opacity: 0.6 }}>
            Cancel
          </ThemedText>
        </Pressable>

        {isLoading && (
          <View
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0,0,0,0.3)',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <ActivityIndicator size="large" color={primaryColor} />
          </View>
        )}
      </ThemedView>
    </Modal>
  );
};
