from PIL import Image
import svgwrite
import numpy as np

def hex_to_rgb(hex_color):
    # Convert hex color to RGB tuple
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def quantize_image(image_path):
    # Define target colors in hex and convert to RGB
    target_colors = {
        "black": hex_to_rgb("12070a"),
        "yellow": hex_to_rgb("eab42e"),
        "red": hex_to_rgb("bf292b")
    }
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        data = np.array(img)
        new_image_data = np.zeros(data.shape, dtype=np.uint8)
        new_image_data[:, :, 3] = data[:, :, 3]  # Preserve the alpha channel
        
        # Map each pixel to the nearest target color using Euclidean distance in RGB space
        for key, color in target_colors.items():
            distance = np.sqrt(np.sum((data[:, :, :3] - np.array(color))**2, axis=-1))
            mask = distance == np.min(np.array([np.sqrt(np.sum((data[:, :, :3] - np.array(target))**2, axis=-1)) for target in target_colors.values()]), axis=0)
            new_image_data[mask, :3] = color

        # Handle white/transparent pixels
        transparent_or_white_mask = (data[:, :, 3] == 0) | np.all(data[:, :, :3] == [255, 255, 255], axis=-1)
        new_image_data[transparent_or_white_mask, :3] = [255, 255, 255]  # Set color to white

        new_img = Image.fromarray(new_image_data, 'RGBA')
        new_img_path = image_path.replace('.png', '_quantized.png')
        new_img.save(new_img_path)
        return new_img_path

def create_svg_and_png_for_color(image_path, color, output_path):
    with Image.open(image_path) as img:
        width, height = img.size
        # Create SVG
        dwg = svgwrite.Drawing(output_path + ".svg", size=(width, height))
        # Create PNG
        new_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))  # Start with a fully transparent image
        pixels = img.load()
        new_pixels = new_image.load()
        
        for x in range(width):
            for y in range(height):
                if pixels[x, y][:3] == color:
                    dwg.add(dwg.circle(center=(x, y), r=0.5, fill=svgwrite.rgb(*color, '%')))
                    new_pixels[x, y] = color + (255,)  # Set pixel as opaque in PNG

        dwg.save()
        new_image.save(output_path + ".png")

def main():
    original_image_path = 'logo.png'
    quantized_image_path = quantize_image(original_image_path)
    colors = [hex_to_rgb(hex_code) for hex_code in ['12070a', 'eab42e', 'bf292b']]  # Convert hex codes to RGB
    colors.append((255, 255, 255))  # Include white

    for color in colors:
        output_path = f'logo_{color}'
        create_svg_and_png_for_color(quantized_image_path, color, output_path)
        print(f'Files created for color {color}: {output_path}.svg and {output_path}.png')

if __name__ == '__main__':
    main()
