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