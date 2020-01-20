library IEEE;
library UNISIM;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;


entity axiFilter is 
port(
  Axi_in_m2s : in  axiStream_32_m2s := axiStream_32_m2s_null;
  Axi_in_s2m : out axiStream_32_s2m := axiStream_32_s2m_null;
  Axi_out_m2s : out axiStream_32_m2s := axiStream_32_m2s_null;
  Axi_out_s2m : in  axiStream_32_s2m := axiStream_32_s2m_null;
  clk :  in  std_logic := '0'
);
end entity;



architecture rtl of axiFilter is


begin

  -----------------------------------
  _process1 : process(clk) is
    variable axiSalve : axiStream_32_slave := axiStream_32_slave_null;
    variable axMaster : axiStream_32_master := axiStream_32_master_null;
    variable i_buff : std_logic_vector(31 downto 0) := (others => '0'); 
    variable axiSalve_buff : std_logic_vector(31 downto 0) := (others => '0'); 
    variable axiSalve_buff : std_logic_vector(31 downto 0) := (others => '0'); 
    begin
      if rising_edge(clk) then 
        pull( axiSalve, Axi_in_m2s);
        pull( axMaster, Axi_out_s2m);
    
        if (( isReceivingData(axiSalve)  and ready_to_send(axMaster) ) ) then 
          read_data(axiSalve, axiSalve_buff ) ;
          i_buff := axiSalve_buff;
          
          if (i_buff < 10) then 
            read_data(axiSalve, axiSalve_buff ) ;
            send_data( axMaster, axiSalve_buff);
            
          end if;
          
        end if;
          push( axiSalve, Axi_in_s2m);
        push( axMaster, Axi_out_m2s);
    end if;
    
    end process;
  
end architecture;