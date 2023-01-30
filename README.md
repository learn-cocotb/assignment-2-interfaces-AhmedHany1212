# Assignment interfaces

This Repo should be used for all assignments following assignment 2.
i.e.

* Interfaces
* TestPlan
* Functional Coverage
* CRV


The DUT Implements an OR Gate with access via a Configuration and Status Register instead of direct access via ports.

## DUT IO specification

The DUT has 2 interfaces Read and Write.

Read Interface takes an address and returns the data at that address.

| Name          | I/O | size |
| ----          | --- | --   |
| read_address  | I   | 3    |
| read_data     | O   | 1    |
| read_rdy      | O   | 1    |
| read_en       | I   | 1    |

Write Interface takes an address and data and writes the data to the address

| Name          | I/O | size |
| ----          | --- | --   |
| write_rdy     | O   | 1    |
| write_address | I   | 3    |
| write_data    | I   | 1    |
| write_en      | I   | 1    |

Clock and Reset Signals

| Name          | I/O | size |
| ----          | --- | --   |
| CLK           | I   | 1    |
| RST_N         | I   | 1    |

# Address map

| Address | Registers | Access | Description                            |
| --      | ------    | --     | --------                               |
| 0       | A_Status  | R      | 1: A Fifo Not Full. 0: Full            |
| 1       | B_Status  | R      | 1: B Fifo Not Full. 0: Full            |
| 2       | Y_Status  | R      | 1: Y Fifo Not Empty. 0: Empty          |
| 3       | y_output  | R      | The output value calculated by the DUT |
| 4       | A_Data    | W      | A Input Data                           |
| 5       | B_Data    | W      | B Input Data                           |
