import React from "react";
import { Pressable, Text } from "react-native";

type Props = {
  title: string;
  onPress?: () => void;
};

export function Button({ title, onPress }: Props) {
  return (
    <Pressable
      onPress={onPress}
      className="items-center justify-center rounded-2xl bg-black px-4 py-3 active:opacity-80"
    >
      <Text className="font-semibold text-white">{title}</Text>
    </Pressable>
  );
}