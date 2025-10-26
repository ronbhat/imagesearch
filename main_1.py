from DeepImageSearch import Load_Data, Search_Setup

dl = Load_Data()

image_list = dl.from_folder(["test-data"])

# Set up the search engine, You can load 'vit_base_patch16_224_in21k', 'resnet50' etc more then 500+ models
st = Search_Setup(image_list, model_name="vgg19", pretrained=True, image_count=None)

# Index the images
#st.run_index()

# Get metadata
metadata = st.get_image_metadata_file()
#st.plot_similar_images("E:/Pictures/100ANDRO/DSC_0043.JPG", number_of_images=6)

no_of_images = len(image_list)

for i in range(no_of_images):
    #for j in range(i+1, no_of_images):
        #print(f"Comparing image {image_list[i]} and {image_list[j]}")
        print(f"Comparing image {image_list[i]}")
        # Get similar images
        print(st.get_similar_images(image_path=image_list[i], number_of_images=10))
        # Plot similar images
        # st.plot_similar_images(image_path=image_list[i], number_of_images=9)

