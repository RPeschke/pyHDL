# PyHDL

## Introduction

PyHDL is a library which allowes one to write Python code and convert it to VHDL. The Main Goal of this library is to allow the user to write fully Object oriented code.

## Getting Started

### Example1

This Example is shows a single entity with two pocess blocks.
- The First process block (```p1```) is a timed block, which means it gets sequentially executed until it reaches the yield statment and then waits for the appropriate time and then continues the execution. In the context of this example ```p1``` works as a clock generator.
- The Second process block (```p2```) is a triggered process block which gets executed evertime the argument of ```rising_edge``` changes. This Process Block updates a signal (```counter```) amd a variable (```v_counter```). Similarly to VHDL the variable gets changed imidatly but is not avalible for any other process. The signal in contrast gets only changed after the process block but can be used in other process blocks. 


```Python
class tb_entity(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()


    def architecture(self):
        clk = v_sl()


        @process()
        def p1():

            @timed()
            def proc():
                clk << 1
                print("set clk to 1")
                yield wait_for(10)
                clk << 1
                yield wait_for(10)
                clk << 0
                yield wait_for(10)

        counter = v_slv(32)
        @process()
        def p2():
            v_counter = v_slv(32)
            @rising_edge(clk)
            def proc():
                v_counter << v_counter +1
                counter << counter + 1
                print("counter", counter.value)
                print("v_counter", v_counter.value)
```

The entity can be simulated running the following commands:

```Python
ax = tb_entity()
gsimulation.run_timed(ax, 1000,"example1.vcd")
```

First one needs to create an instants of the entity and then it has to be given as an argument to the simulator alongside the runtime and the output file name. The ouput file can then be viewed with programs like ```GTKWave```.

![GTKWave](pictures/example1.png)

In Addition the program can be converted to ```VHDL``` using the following command:

```Python
print(ax._get_definition())
```

The output is the following:

```vhdl

entity tb_entity is 
end entity;



architecture rtl of tb_entity is

signal clk : std_logic := '0'; 
signal counter : std_logic_vector(31 downto 0) := (others => '0'); 

begin

  -----------------------------------
  p1 : process
    begin
      clk <= '1';
      wait for  10 ns;
      clk <= '1';
      wait for  10 ns;
      clk <= '0';
      wait for  10 ns;
    end process;
  
  -----------------------------------
  p2 : process(clk) is
    variable v_counter : std_logic_vector(31 downto 0) := (others => '0');
    begin
      if rising_edge(clk) then
        v_counter := v_counter + 1;
        counter <= counter + 1;
      end if;
    end process;
  
end architecture;
```

As one can see the Converted can figure out by itself if a given symbol is a signal or a variable. Also the print statements are currently not supported. Usually if the converter encounters an unknown token it would raise an Exception. For Print there has been written a special module which tells the converter to silently ignore it. 


### Example2

This Example shows how multiple entities can interact with each other. 
1. Clock Generation has been moved to its own entity. 
1. A new entity was introduced that allows to print out data from an axi stream interface. This entity shows the value of the buffer before and after the it has been changed. 
1. the communication between the individual entities is done with classes. With this approach the user does not need to know which signals flow between the different entities. The user can just utilize a library and focus on the actual logic that needs to be implemented. 

```Python
class axiPrint(v_clk_entity):
    def __init__(self,clk=None):
        super().__init__(__file__, clk)
        self.Axi_in = port_Slave(axisStream(32,v_slv(32)))
        self.architecture()

        
    def architecture(self):
        @process()
        def _process1():
            axiSalve = axisStream_slave(self.Axi_in)

            i_buff = v_slv(32)

            @rising_edge(self.clk)
            def proc():
                print("axiPrint",i_buff.value )
                if axiSalve :
                    i_buff << axiSalve
                    print("axiPrint valid",i_buff.value )



class clk_generator(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.clk = port_out(v_sl())
        self.architecture()

    def architecture(self):
        
        @process()
        def p1():

            @timed()
            def proc():
                self.clk << 1
                print("======================")
                yield wait_for(10)
                self.clk << 0
                yield wait_for(10)


class tb_entity(v_entity):
    def __init__(self):
        super().__init__(__file__)
        self.architecture()
        


    def architecture(self):
        clkgen = v_create(clk_generator())

        Axi_out = axisStream(32,v_slv(32))
        counter = v_slv(32)
        axFil = v_create(axiPrint(clkgen.clk))
        axFil.Axi_in << Axi_out


        @process()
        def p2():
            v_Axi_out = axisStream_master(Axi_out)
            @rising_edge(clkgen.clk)
            def proc():
                if v_Axi_out and counter < 40:
                    print("counter", counter.value)
                    v_Axi_out << counter
                
                    counter << counter + 1
```

This example can be simulated with the following command:

```Py
ax = tb_entity()
gsimulation.run_timed(ax, 1000,"example2.vcd")
```

Each individual entity can be converted to VHDL by using the following command:


```Py
ax = tb_entity()
print(ax._get_definition())
```
The output from this is the following VHDL code:

```VHDL
entity tb_entity is 
end entity;



architecture rtl of tb_entity is

signal clkgen_clk : std_logic := '0'; 
signal Axi_out_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal Axi_out_s2m : axisStream_32_s2m := axisStream_32_s2m_null;
signal counter : std_logic_vector(31 downto 0) := (others => '0'); 
signal axFil_Axi_in_m2s : axisStream_32_m2s := axisStream_32_m2s_null;
signal axFil_Axi_in_s2m : axisStream_32_s2m := axisStream_32_s2m_null;

begin
clkgen : entity work.clk_generator port map ( 
      clk => clkgen_clk
  );
  axFil : entity work.axiPrint port map ( 
      Axi_in_m2s => axFil_Axi_in_m2s, 
      Axi_in_s2m => axFil_Axi_in_s2m,
      clk => clkgen_clk
  );
  ---------------------------------------------------------------------
  --  axFil_Axi_in << Axi_out
  axFil_Axi_in_s2m <= Axi_out_s2m;
  Axi_out_m2s <= axFil_Axi_in_m2s;
  
  -----------------------------------
  p2 : process(clkgen_clk) is
    begin
      if rising_edge(clkgen_clk) then 
        pull( v_Axi_out, Axi_out_s2m);
    
        if (( ready_to_send(v_Axi_out)  and counter < 40) ) then 
          send_data( v_Axi_out, counter);
          counter <= counter + 1;
          
        end if;
          push( v_Axi_out, Axi_out_m2s);
    end if;
    
    end process;
  
end architecture;
```



## Object Oriented Desigen for HDL

Virtually all modern programming languages allow the user to write customised objects to build powerful abstraction. The support for this is very limited in typical HDLs. This document is ment to show the limitations of current HDLs and especially how adding an additional layer of abstraction in form of PyHDL can overcome this limitation.

## Limitations of current HDL

### The strict IN/OUT model

Typical HDLs are build up of submodules. In the case of VHDL this submodules are called ```entities```. These ```entites``` are connected to each other by ports. A port can be a single bit (```std_logic```), an array of bits (```std_logic_vector```), a data structure (```record```) or an array of data structure. But no matter how complicated the individual port is, it has always to be labeled as either ```IN``` or ```OUT```. This strict seperation between ```IN``` and ```OUT``` 
