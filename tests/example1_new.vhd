library IEEE;
library UNISIM;
use IEEE.numeric_std.all;
use IEEE.std_logic_1164.all;
use UNISIM.VComponents.all;
use ieee.std_logic_unsigned.all;


entity rollingCounter is 
port(
  Axi_out_m2s : out axiStream_32_m2s := axiStream_32_m2s_null;
  Axi_out_s2m : in  axiStream_32_s2m := axiStream_32_s2m_null;
  MaxCount :  in  std_logic_vector(31 downto 0) := x"0000000a";
  clk :  in  std_logic := '0'
);
end entity;



architecture rtl of rollingCounter is

signal counter : std_logic_vector(32 -1 downto 0) := (others => '0'); 

begin

  -----------------------------------
  p2 : process(clk) is
    variable v_Axi_out : axiStream_32_master := axiStream_32_master_null;
    begin
      if rising_edge(clk) then 
        pull( v_Axi_out, Axi_out_s2m);
    
        if (ready_to_send(v_Axi_out) ) then 
          send_data( v_Axi_out, counter);
          counter <= counter + 1;
          
        end if;
      
        if (counter > MaxCount) then 
          counter <=  (others => '0');
          
        end if;
          push( v_Axi_out, Axi_out_m2s);
    end if;
    
    end process;
  
end architecture;