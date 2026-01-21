from scipy import io
import os
import shutil

# 两个文件的关联关系:
# 验证集图片: ILSVRC2012_val_00000001.JPEG
# ↓
# 标签文件: 第1行 -> 154 (数字标签)
# ↓
# 元数据: ID=154 -> WNID=n01440764, 描述="tench, Tinca tinca"
# ↓
# 文件夹: n01440764 --> 存放对应图片ILSVRC2012_val_00000001.JPEG

def move_valimg(val_dir='../val', devkit_dir='../ILSVRC2012_devkit_t12'):
    """
    move valimg to correspongding folders.
    val_id(start from 1) -> ILSVRC_ID(start from 1) -> WIND
    organize like:
    /val
       /n01440764
           ILSVRC2012_val_00000001.JPEG
       /n01443537
           ...
        .....
    """
    # load synset, val ground truth and val images list
    synset = io.loadmat(os.path.join(devkit_dir, 'data', 'meta.mat'))
    ground_truth = open(os.path.join(devkit_dir, 'data', 'ILSVRC2012_validation_ground_truth.txt'))
    
    lines = ground_truth.readlines()
    labels = [int(line[:-1]) for line in lines]
    
    root, _, filenames = next(os.walk(val_dir))
    # collect map_info
    map_info = []
    for filename in filenames:
        # val image name -> ILSVRC ID -> WIND
        val_id = int(filename.split('.')[0].split('_')[-1])
        ILSVRC_ID = labels[val_id-1]
        WIND = synset['synsets'][ILSVRC_ID-1][0][1][0]
        # print("val_id:%d, ILSVRC_ID:%d, WIND:%s" % (val_id, ILSVRC_ID, WIND))
        map_info.append((val_id, filename, ILSVRC_ID, WIND))
        
        """
        val_id:2733, ILSVRC_ID:538, WIND:n02879718
        val_id:45927, ILSVRC_ID:561, WIND:n04372370
        val_id:14620, ILSVRC_ID:488, WIND:n01748264
        """

        # move val images
        output_dir = os.path.join(root, WIND)
        if os.path.isdir(output_dir):
            pass
        else:
            os.mkdir(output_dir)
        shutil.move(os.path.join(root, filename), os.path.join(output_dir, filename))
    # print("root:%s" % root)  
    
    # 建立WIND的文件夹排序映射count
    count = 0
    wind_to_count = dict()
    unique_winds = sorted(
        set([info[3] for info in map_info]),    # 提取所有WIND并去重
        key=lambda x: int(x[1:])                # 按数字部分排序（去掉开头的'n'）
    )
    for wind in unique_winds:
        wind_to_count[wind] = count
        count += 1
    for i, (val_id, filename, ILSVRC_ID, WIND) in enumerate(map_info):
        map_info[i] = (val_id, filename, ILSVRC_ID, WIND, wind_to_count[WIND])

    # ranking by val_id
    map_info.sort(key=lambda x: x[0])
    for val_id, filename, ILSVRC_ID, WIND, count in map_info:
        # print("val_id:%d, FILE:%s, ILSVRC_ID:%d, WIND:%s, count:%d" % (val_id, filename.split('.')[0], ILSVRC_ID, WIND, count))
        print("%s %d" % (filename.split('.')[0], count))

if __name__ == '__main__':
    move_valimg()
