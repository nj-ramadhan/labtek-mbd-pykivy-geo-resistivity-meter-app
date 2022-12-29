import numpy as np

STEPS = 51
MAX_POINT = 3000
ELECTRODES_NUM = 48

dt_distance = 1
dt_constant = 1

x_datum = np.zeros(MAX_POINT)
y_datum = np.zeros(MAX_POINT)
x_electrode = np.zeros((4, MAX_POINT))
n_electrode = np.zeros((ELECTRODES_NUM, STEPS))
c_electrode = np.array(["#196BA5","#FF0000","#FFDD00","#00FF00","#00FFDD"])
l_electrode = np.array(["Datum","C1","C2","P1","P2"])

nmax_available = 0
if(ELECTRODES_NUM % 2) != 0:
    if(dt_constant > (ELECTRODES_NUM - 3) / 2):
        nmax_available = (ELECTRODES_NUM - 3) / 2
    else:
        nmax_available = dt_constant
else:
    if(dt_constant > (ELECTRODES_NUM - 3) / 2):
        nmax_available = round((ELECTRODES_NUM - 3) / 2)
    else:
        nmax_available = dt_constant
print(nmax_available)

num_datum = 0
count_datum = 0      
for i in range(nmax_available):
    for j in range(ELECTRODES_NUM - 1 - i * 2):
        num_datum = num_datum + j
    count_datum = count_datum + num_datum
    num_datum = 0     
print(count_datum)

num_step = 1
num_trial = 1
for i in range(nmax_available):
    for j in range(ELECTRODES_NUM - 1 - i * 2):
        for k in range(ELECTRODES_NUM - i * 2 - j):
            x_electrode[1, num_step] = j
            x_electrode[0, num_step] = j + 1 + (i - 1)
            x_electrode[2, num_step] = num_trial + x_electrode[0, num_step]
            x_electrode[3, num_step] = i + x_electrode[2, num_step]
            x_datum[num_step] = (x_electrode[0, num_step] + (x_electrode[2, num_step] - x_electrode[0, num_step])/2) * dt_distance
            y_datum[num_step] = (i + 1) * dt_distance
            # print("x:"+ str(x_datum[num_step]) + " y:"+ str(y_datum[num_step]))
            num_step += 1
            num_trial += 1
        num_trial = 0

x_data = np.trim_zeros(x_datum)
y_data = np.trim_zeros(y_datum)
print(x_data.shape)
print(y_data.shape)

data_base = np.zeros([2, 1])
print(data_base)

for i in range(20):
    data_acquisition = np.array([np.random.random_sample(), np.random.random_sample()])
    temp_data_acquisition = data_acquisition
    temp_data_acquisition.resize([2, 1])
    data_base = np.concatenate([data_base, temp_data_acquisition], axis=1)
    # np.append(data_base, temp_data_acquisition, axis=1)
    print(data_acquisition)

print(data_base)