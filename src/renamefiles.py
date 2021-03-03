import sys
import os
import csv
import click # pip install -U click
from loguru import logger # pip install loguru
import yaml # pip install pyyaml

class Baseclass:
    options = None
    def __init__(self,**kwargs):
        # super().__init__(**kwargs)
        for k,v in kwargs.items():
            if v is not None:
                setattr(self,k,v)
class Config(Baseclass):
    '''Base configuration.'''
    config_directory = None
    config_filename = "renamefiles.yaml"
    debug_out_filename = "renamefiles.txt"
    config = None
    debug_out_filepath = None
    fh = None
    delete_debug = True
    verbose_debug = True
    rename_base = ''
    rename_padding = '00000'
    data_path = None # for the linter
    debug_out = None # for the linter
    extension = None # linter
    def __init__(self,**kwargs):
        assert os.path.exists(self.config_filename), f"config_filename does not exist, got {self.config_filename}"
        with open(self.config_filename ,'r') as fh:
            theconfig = yaml.load(fh,Loader=yaml.FullLoader)
            if theconfig:
                for k,v in theconfig.items():
                    setattr(self,k.replace('-','_'),v)
        super().__init__(**kwargs)
        if self.data_path:
            self.debug_out_filepath = os.path.join(self.data_path,self.debug_out_filename)
            try:
                os.remove(self.debug_out_filepath)
            except:
                pass

class RenamefilesHandler(Baseclass):
    config = None
    f = None
    def __init__(self,**kwargs):
        f = None
        self.config = Config(data_path = kwargs.pop('data_path',None) )
        super().__init__(**kwargs)
  
    def listfiles(self):
        with open(self.config.debug_out_filepath, 'a', newline='\n', encoding='UTF-8') as self.f:
            for filename in os.listdir(self.config.data_path):
                if ( not os.path.isfile(os.path.join(self.config.data_path, filename)) or  
                        filename == self.config.data_path ):
                    continue
                filesplit = os.path.splitext(filename)
                if self.config.extension:
                    if filesplit[1] != '.' + self.config.extension:
                        continue
                self.writeout(filename)
     
    def renamefiles(self):
        i = 0
        with open(self.config.debug_out_filepath, 'a', newline='\n', encoding='UTF-8') as self.f:
            for filename in os.listdir(self.config.data_path):
                if ( not os.path.isfile(os.path.join(self.config.data_path, filename)) or  
                        filename == self.config.data_path ):
                    continue
                filesplit = os.path.splitext(filename)
                if self.config.extension:
                    if filesplit[1] != '.' + self.config.extension:
                        continue
                i += 1
                while True:
                    newfilenumber = self.config.rename_padding + str(i)
                    newfilenumber = newfilenumber[ - len(self.config.rename_padding) - 1:]
                    newfilename = self.config.rename_base + newfilenumber + filesplit[1]
                    if not os.path.isfile(os.path.join(self.config.data_path, newfilename) ):
                        break
                    i = i + 1
                os.rename( os.path.join(self.config.data_path, filename) , os.path.join(self.config.data_path, newfilename) )
                self.writeout(f"{filename} => {newfilename}")

    def writeout(self,message):
        print(message)
        print(message, file=self.f)

@click.group()
@click.option('--debug', is_flag=True)
@click.option('--trace', is_flag=True)
@click.pass_context
def cli(ctx,debug,trace):
    """ad hoc handler"""
    ctx.obj['debug'] = debug
    ctx.obj['trace'] = trace
    if debug:
        logger.remove(0)
        logger.add(sys.stdout, level='DEBUG')
    if trace:
        logger.remove(0)
        logger.add(sys.stdout, level='TRACE')
    if not debug and not trace:
        logger.remove(0)
        logger.add(sys.stdout, level='INFO')

@cli.command('test')
@click.argument('command', default='')
@click.pass_context
def test(ctx, command):
    print("a test")

@cli.command('rename')
@click.argument('path', default='')
@click.option('--extension')
@click.pass_context
def rename(ctx,path,extension):
    print("renaming")
    renamehandler = RenamefilesHandler(data_path=path)
    renamehandler.config.extension = extension
    renamehandler.renamefiles()

if __name__ == '__main__':
    cli(obj={})
