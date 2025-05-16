import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import glob
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

def read_asc(file_path):
    with open(file_path, 'r') as file:
        header = [file.readline().strip() for _ in range(6)]
        data = np.loadtxt(file)
    return header, data

def write_asc(file_path, header, data):
    with open(file_path, 'w') as file:
        for line in header:
            file.write(line + '\n')
        np.savetxt(file, data, fmt="%.2f")

def select_file(prompt, available_files):
    print(f"\n{prompt}")
    for i, file in enumerate(available_files, 1):
        print(f"{i}. {file}")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the file: "))
            if 1 <= choice <= len(available_files):
                return available_files[choice - 1]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Please enter a valid number.")

def generate_comparison(target_data, source_data):
    difference = source_data - target_data
    
    # Calculate statistics
    mean_diff = np.mean(difference)
    std_diff = np.std(difference)
    min_diff = np.min(difference)
    max_diff = np.max(difference)
    
    # Create comparison visualization
    current_date = datetime.now().strftime('%Y%m%d')
    comparison_filename = f'comparison_{current_date}.png'
    
    plt.figure(figsize=(15, 10))
    
    # Plot target data
    plt.subplot(221)
    plt.title("Target Heightmap")
    plt.imshow(target_data, cmap="terrain")
    plt.colorbar()
    
    # Plot source data
    plt.subplot(222)
    plt.title("Source Heightmap")
    plt.imshow(source_data, cmap="terrain")
    plt.colorbar()
    
    # Plot difference
    plt.subplot(223)
    im = plt.imshow(difference, cmap='RdYlBu')
    plt.title("Difference Map")
    plt.colorbar(im, label='Elevation Difference')
    
    # Add statistics
    stats_text = f'Statistics:\nMean Difference: {mean_diff:.2f}\nStd Deviation: {std_diff:.2f}\n'
    stats_text += f'Min Difference: {min_diff:.2f}\nMax Difference: {max_diff:.2f}'
    plt.subplot(224)
    plt.text(0.1, 0.5, stats_text, fontsize=12)
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(comparison_filename, dpi=300, bbox_inches='tight')
    print(f"\nComparison saved as: {comparison_filename}")
    plt.show()
    
    return comparison_filename

def process_merge(target_file, source_file, mask_file):
    # Load heightmaps
    target_header, target_data = read_asc(target_file)
    source_header, source_data = read_asc(source_file)
    
    # Load and process mask
    mask_image = Image.open(mask_file).convert("RGB")
    mask_array = np.array(mask_image)
    
    # Resize mask if dimensions don't match
    if mask_array.shape[:2] != target_data.shape:
        print(f"\nResizing mask to match heightmap dimensions: {target_data.shape}")
        mask_image = mask_image.resize((target_data.shape[1], target_data.shape[0]))
        mask_array = np.array(mask_image)
    
    # Create mask from pure red pixels (255, 0, 0)
    mask = (mask_array[:,:,0] == 255) & (mask_array[:,:,1] == 0) & (mask_array[:,:,2] == 0)
    
    # Apply the mask
    merged_data = target_data.copy()
    merged_data[mask] = source_data[mask]
    
    # Generate output filename
    current_date = datetime.now().strftime('%Y%m%d')
    output_asc = f'merged_{current_date}.asc'
    
    # Save the merged ASC file
    write_asc(output_asc, target_header, merged_data)
    print(f"\nMerged ASC file saved as: {output_asc}")
    
    # Create final visualization
    plt.figure(figsize=(15, 5))
    
    plt.subplot(131)
    plt.title("Target Heightmap")
    plt.imshow(target_data, cmap="terrain")
    plt.colorbar()
    
    plt.subplot(132)
    plt.title("Applied Mask")
    plt.imshow(mask, cmap="gray")
    
    plt.subplot(133)
    plt.title("Merged Result")
    plt.imshow(merged_data, cmap="terrain")
    plt.colorbar()
    
    viz_filename = f'merge_visualization_{current_date}.png'
    plt.tight_layout()
    plt.savefig(viz_filename, dpi=300, bbox_inches='tight')
    print(f"Final visualization saved as: {viz_filename}")
    plt.show()

def main():
    # Get list of files
    asc_files = glob.glob("*.asc")
    png_files = glob.glob("*.png")
    
    if len(asc_files) < 2:
        print("Need at least 2 .asc files in the current directory!")
        exit()
    
    # First select the mask file
    png_files = glob.glob("*.png")
    if not png_files:
        print("No PNG mask files found in the current directory!")
        exit()
    
    print("\nSelect the mask file (should contain pure red RGB(255,0,0) areas to indicate merge regions):")
    mask_file = select_file("Select the mask PNG file:", png_files)
    
    # Select ASC files
    print("\nSelect the target ASC file (file to be modified):")
    target_file = select_file("Select the target .asc file:", asc_files)
    
    remaining_files = [f for f in asc_files if f != target_file]
    print("\nSelect the source ASC file (file to take data from):")
    source_file = select_file("Select the source .asc file:", remaining_files)
    
    # Load data for comparison
    target_header, target_data = read_asc(target_file)
    source_header, source_data = read_asc(source_file)
    
    # Generate and display comparison
    comparison_file = generate_comparison(target_data, source_data)
    
    # Inform user about the mask requirements
    messagebox.showinfo("Mask Requirements", 
        "Please ensure your mask file uses pure red (RGB: 255,0,0)\n"
        "to indicate areas where data should be merged from the source file.")
    
    # Process the merge
    process_merge(target_file, source_file, mask_file)

if __name__ == "__main__":
    main() 