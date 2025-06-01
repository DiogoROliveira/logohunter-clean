import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os

def create_logo_variations(input_path, output_dir, base_filename):
    """
    Create various modifications of a logo image that might fool the detector
    while still being recognizable to humans.
    
    Args:
        input_path (str): Path to the input logo image
        output_dir (str): Directory to save the modified logos
        base_filename (str): Base name for the output files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the image
    original = Image.open(input_path)
    
    # 1. Subtle Rotation
    for angle in [2, -2, 5, -5]:
        rotated = original.rotate(angle, expand=True)
        rotated.save(os.path.join(output_dir, f"{base_filename}_rotated_{angle}.png"))
    
    # 2. Slight Color Modifications
    img_array = np.array(original)
    
    # HSV modification
    if len(img_array.shape) == 3:  # Only for color images
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        # Modify hue slightly
        hsv[:,:,0] = (hsv[:,:,0] + 10) % 180
        modified = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        Image.fromarray(modified).save(os.path.join(output_dir, f"{base_filename}_color_shift.png"))
    
    # 3. Add Subtle Noise
    noise = np.random.normal(0, 2, img_array.shape).astype(np.uint8)
    noisy = cv2.add(img_array, noise)
    Image.fromarray(noisy).save(os.path.join(output_dir, f"{base_filename}_noise.png"))
    
    # 4. Blur Edges
    blurred = original.filter(ImageFilter.GaussianBlur(radius=0.5))
    blurred.save(os.path.join(output_dir, f"{base_filename}_blurred.png"))
    
    # 5. Contrast Modification
    enhancer = ImageEnhance.Contrast(original)
    contrast_img = enhancer.enhance(0.8)  # Slightly reduce contrast
    contrast_img.save(os.path.join(output_dir, f"{base_filename}_contrast.png"))
    
    # 6. Scale Modification (slight stretching)
    width, height = original.size
    stretched = original.resize((int(width * 1.1), height))
    stretched.save(os.path.join(output_dir, f"{base_filename}_stretched.png"))
    
    # 7. Edge Enhancement
    edge_enhanced = original.filter(ImageFilter.EDGE_ENHANCE)
    edge_enhanced.save(os.path.join(output_dir, f"{base_filename}_edge_enhanced.png"))
    
    # 8. Combination of modifications
    combo = Image.fromarray(noisy).rotate(3)
    combo = combo.filter(ImageFilter.GaussianBlur(radius=0.3))
    combo.save(os.path.join(output_dir, f"{base_filename}_combo.png"))

def main():
    # Lista de logos para processar
    logos = [
        "adidas",
        "nike",
        "lexus",
        "golden_state_warriors",
        "duff_beer",
        "puma",
        "underarmour",
        "wellsfargo",
        "robin",
        "champion",
        "aldi"
    ]
    
    # Diretório base para os logos originais e modificados
    input_base = "data/original_logos"
    output_base = "data/modified_logos"
    
    # Criar diretório de saída se não existir
    os.makedirs(output_base, exist_ok=True)
    
    # Processar cada logo
    for logo in logos:
        print(f"Procurando imagens para {logo}...")
        
        # Listar todos os arquivos no diretório de entrada
        input_files = [f for f in os.listdir(input_base) if f.lower().startswith(logo.lower()) and 
                      f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not input_files:
            print(f"Nenhuma imagem encontrada para {logo}")
            continue
            
        print(f"Encontradas {len(input_files)} imagens para {logo}")
        
        # Processar cada imagem encontrada
        for input_file in input_files:
            input_path = os.path.join(input_base, input_file)
            output_dir = os.path.join(output_base, logo)
            base_filename = os.path.splitext(input_file)[0]
            
            print(f"  Processando {input_file}...")
            try:
                create_logo_variations(input_path, output_dir, base_filename)
            except Exception as e:
                print(f"    Erro ao processar {input_file}: {str(e)}")

if __name__ == "__main__":
    main() 