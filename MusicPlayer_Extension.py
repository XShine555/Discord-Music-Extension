
from discord.ext import commands as DiscCommands, tasks as DiscTasks
from discord import ui as DiscUi
from discord import ButtonStyle
from discord import Interaction
from discord import Embed
import discord as Disc
import json as Json
import pomice as Pomice

class MusicPlayer_Extension(DiscCommands.Cog):

    def __init__(Self, Bot) -> None:
        
        Self.Bot = Bot

        Self.VoiceBot = None

        Self.TextBot = None

        Self.EditMessage = None

        Self.Queue = Pomice.Queue()

        # We use our LoopMode function because its more simple and it includes some benefits.

        Self.LoopMode = None

        Self.IsSkiped = False

    # This functions permit to make the bot Multi-Language.

    async def getLocale(Self, Context, Locale):

        # This version doesn't include Database Support. That's why there is a Language Var :)
        
        Language = 'En'

        File = open('MusicPlayer_Locale.json', encoding = 'UTF-8')
        Read = Json.load(File)

        ToReturn = Read[Language][Locale]

        if ToReturn is None:

            return f'{Locale} Is Missing!'

        return ToReturn
    
    # Play, Pause, Stop And Resume Functions.

    @DiscCommands.command(name = 'Play')

    async def Play(Self, Context : DiscCommands.Context, *, Search):

        # Author Not Connected
        
        if Context.author.voice is None:

            return await Context.send( await Self.getLocale(Context, 'Author_Not_Connected') )

        # None --> Connect

        if Context.voice_client is None:

            Self.TextBot : DiscCommands.Context = Context

            Self.VoiceBot : Pomice.Player = await Context.author.voice.channel.connect(cls = Pomice.Player)

        # But If Is Already In Channel.

        else:
            
            anyInVoice = False

            for User in Context.author.voice.channel.members:

                if not User.bot:
                
                    anyInVoice = True
                    
                    break

            isAuthor = Context.author.voice.channel.id is Context.voice_client.channel.id

            # 1. Move the bot.

            if not anyInVoice and not isAuthor:

                if Self.VoiceBot.is_playing:

                    Self.VoiceBot.stop()

                if not Self.Queue.is_empty:

                    Self.Queue.clear()

                Self.VoiceBot.move_to(Context.author.voice.channel.id)

            if anyInVoice and not isAuthor:

                return await Context.send( await Self.getLocale(Context, 'Already_In_Use') )

        # 3. Already in the same channel.

        Search = await Self.VoiceBot.get_tracks(query = f'{Search}')

        if not Search:

            return await Context.send( await Self.getLocale(Context, 'Search_Not_Found') )

        if isinstance(Search, Pomice.Playlist):

            for Track in Search.tracks:

                Self.Queue.put(Track)

        else:

            Self.Queue.put(Search[0])

            await Context.send( await Self.getLocale(Context, 'Added_To_Queue') + f'```{Search[0].title}```' )

        if not Self.VoiceBot.is_playing:

            await Self.VoiceBot.play(Self.Queue.get())

    async def Pause(Self, Context : DiscCommands.Context):

        # Author Not Connected

        if Context.author.voice is None:

            return await Context.send( await Self.getLocale(Context, 'Author_Not_Connected') )

        # None --> Send Message.

        if Context.voice_client is None:

            return await Context.send( await Self.getLocale(Context, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Context.author.voice.channel.id is Context.voice_client.channel.id

            if not isAuthor:

                return await Context.send( await Self.getLocale(Context, 'Not_The_Same_Channel') )

            if not Self.VoiceBot.is_paused:

                return await Context.send( await Self.getLocale(Context, 'Player_Already_Stopped') )
            
        await Self.VoiceBot.set_pause(True)

    async def Resume(Self, Context : DiscCommands.Context):

        # Author Not Connected

        if Context.author.voice is None:

            return await Context.send( await Self.getLocale(Context, 'Author_Not_Connected') )

        # None --> Send Message.

        if Context.voice_client is None:

            return await Context.send( await Self.getLocale(Context, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Context.author.voice.channel.id is Context.voice_client.channel.id

            if not isAuthor:

                return await Context.send( await Self.getLocale(Context, 'Not_The_Same_Channel') )
            
            if not Self.VoiceBot.is_paused:

                return await Context.send( await Self.getLocale(Context, 'Player_Not_Stopped') )
            
        await Self.VoiceBot.set_pause(False)

    async def Leave(Self, Context : DiscCommands.Context):

        # None --> Send Message.

        if Context.voice_client is None:

            return await Context.send( await Self.getLocale(Context, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:
            
            anyInVoice = False

            for User in Context.author.voice.channel.members:

                if not User.bot:
                
                    anyInVoice = True
                    
                    break

            isAuthor = Context.author.voice.channel.id is Context.voice_client.channel.id

            #1. Bot Alone.

            if not anyInVoice or isAuthor:

                return await Self.VoiceBot.destroy()
            
            return await Context.send( await Self.getLocale(Context, 'Not_The_Same_Channel"') )

    async def DoNext(Self, Context : DiscCommands.Context):

        # Author Not Connected

        if Context.author.voice is None:

            return await Context.send( await Self.getLocale(Context, 'Author_Not_Connected') )

        # None --> Send Message.

        if Context.voice_client is None:

            return await Context.send( await Self.getLocale(Context, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Context.author.voice.channel.id is Context.voice_client.channel.id

            if isAuthor:

                if Self.Queue.is_empty:

                    return await Context.send( await Self.getLocale(Context, 'Queue_Empty') )
                
                else:

                    Self.VoiceBot.play(Self.Queue.get())
                
    @DiscCommands.command(name = 'Repeat')
                
    async def Repeat(Self, Context : DiscCommands.Context):

        # Author Not Connected

        if Context.author.voice is None:

            return await Context.send( await Self.getLocale(Context, 'Author_Not_Connected') )

        # None --> Send Message.

        if Context.voice_client is None:

            return await Context.send( await Self.getLocale(Context, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Context.author.voice.channel.id is Context.voice_client.channel.id

            if isAuthor:

                if Self.Queue.is_looping:

                    Self.Queue.disable_loop()

                    # Also we need to remove the Song that is currently looping.

                    #Self.Queue.remove(Self.VoiceBot.current)

                    return await Context.send( await Self.getLocale(Context, 'LoopMode_Disabled') )

                else:

                    # We Setup the player in LoopMode, but we need to add the current song to the Queue.

                    #Self.Queue.set_loop_mode(mode = Pomice.LoopMode.TRACK)

                    #Self.Queue.put(Self.VoiceBot.current)

                    Self.LoopMode = Pomice.LoopMode.TRACK

                    return await Context.send( await Self.getLocale(Context, 'LoopMode_Activated') )
                
    @DiscCommands.command(name = 'Seek')

    async def Seek(Self, Context : DiscCommands.Context, Time):

        # Author Not Connected

        if Context.author.voice is None:

            return await Context.send( await Self.getLocale(Context, 'Author_Not_Connected') )

        # None --> Send Message.

        if Context.voice_client is None:

            return await Context.send( await Self.getLocale(Context, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Context.author.voice.channel.id is Context.voice_client.channel.id

            if isAuthor:
                
                if Self.VoiceBot.is_playing:

                    # Try to convert the Str into Int.

                    try:

                        Time = int(Time)

                        Time *= 1000 # Seconds to Miliseconds.

                    except ValueError:

                        return await Context.send( await Self.getLocale(Context, 'Enter_Valid_Number') )
                    
                    # If is -1... or +Than the current track, return an error.

                    if Time < 0 or Time > Self.VoiceBot.current.length:

                        return await Context.send( await Self.getLocale(Context, 'Enter_Valid_Number') )

                    await Self.VoiceBot.seek(Time)

                else:

                    return await Context.send( await Self.getLocale(Context, 'Nothing_Playing') )

    @DiscCommands.Cog.listener()

    async def on_pomice_track_start(Self, Player : Pomice.Player, Track):

        # This will be add buttons when a new song is playing.

        LeaveButton = DiscUi.Button(style = ButtonStyle.grey, label = await Self.getLocale(Player, 'Leave'))
        PauseButton = DiscUi.Button(style = ButtonStyle.red, label = await Self.getLocale(Player, 'Pause'))
        SkipButton = DiscUi.Button(style = ButtonStyle.blurple, label = await Self.getLocale(Player, 'Skip'))
        ListButton = DiscUi.Button(style = ButtonStyle.blurple, label = await Self.getLocale(Player, 'List'))

        newView = DiscUi.View(timeout = None)
        newView.add_item(LeaveButton)
        newView.add_item(PauseButton)
        newView.add_item(SkipButton)
        newView.add_item(ListButton)

        LeaveButton.callback = Self.onLeaveButton
        PauseButton.callback = Self.onPauseButton
        SkipButton.callback = Self.onSkipButton
        ListButton.callback = Self.onListButton

        Self.EditMessage = await Self.TextBot.send( await Self.getLocale(Player, 'Now_Playing') + f'{Player.current.title}', view = newView )

    @DiscCommands.Cog.listener()

    async def on_pomice_track_end(Self, Player : Pomice.Player, Track, _):

        await Self.EditMessage.edit(view = None)

        if Self.LoopMode is Pomice.LoopMode.TRACK and not Self.IsSkiped:

            await Self.VoiceBot.play(Track)

        elif not Self.Queue.is_empty:

            await Self.VoiceBot.play(Self.Queue.get())

        Self.IsSkiped = False

        #if not Self.Queue.is_empty:

            #await Self.VoiceBot.play(Self.Queue.get())
    
    @DiscCommands.Cog.listener() 

    async def on_voice_state_update(Self, Member, Before, After):

        if Member != Self.Bot.user:

            return

        if Before.channel and After.channel is None:

            await Self.EditMessage.edit(view = None)

        if Before.channel is None and After.channel and not Member.voice.deaf:

            await Member.edit(deafen = True)

        if Before.deaf and not After.deaf:

            await Member.edit(deafen = True)

            await Self.TextBot.send( await Self.getLocale(Member, 'Dont_Undeaf') )

    # Callbacks for buttons to work.

    async def onLeaveButton(Self, Interaction : Interaction):

        #Author Not Connected
        
        if Interaction.user.voice is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Author_Not_Connected') )

        # None --> Send Message.

        if Interaction.guild.voice_client is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Interaction.user.voice.channel.id is Interaction.guild.voice_client.channel.id

            if isAuthor:

                await Self.VoiceBot.destroy()

                Self.Queue.clear()

                Interaction.response.is_done()

            else:

                return await Interaction.response.send_message(content = await Self.getLocale(Interaction, 'Not_The_Same_Channel') )

    async def onPauseButton(Self, Interaction : Interaction):

        #Author Not Connected
        
        if Interaction.user.voice is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Author_Not_Connected') )

        # None --> Send Message.

        if Interaction.guild.voice_client is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Interaction.user.voice.channel.id is Interaction.guild.voice_client.channel.id

            if isAuthor:

                # The new button will use the same callback, also we need to create all the buttons again.

                LeaveButton = DiscUi.Button(style = ButtonStyle.grey, label = await Self.getLocale(Interaction, 'Leave'))
                PauseOrResumeButton = DiscUi.Button(style = ButtonStyle.red, label = await Self.getLocale(Interaction, 'Pause'))
                SkipButton = DiscUi.Button(style = ButtonStyle.blurple, label = await Self.getLocale(Interaction, 'Skip'))

                # Now we check Pause button state.

                if not Self.VoiceBot.is_paused:

                    PauseOrResumeButton = DiscUi.Button(style = ButtonStyle.green, label = await Self.getLocale(Interaction, 'Resume'))

                    await Self.VoiceBot.set_pause(True)

                else:

                    await Self.VoiceBot.set_pause(False)

                newView = DiscUi.View(timeout = None)
                newView.add_item(LeaveButton)
                newView.add_item(PauseOrResumeButton)
                newView.add_item(SkipButton)

                LeaveButton.callback = Self.onLeaveButton
                PauseOrResumeButton.callback = Self.onPauseButton
                SkipButton.callback = Self.onSkipButton

                await Interaction.response.edit_message(view = newView)

            else:

                return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Im_Not_Connected') )

    async def onSkipButton(Self, Interaction : Interaction):

        # Author Not Connected
        
        if Interaction.user.voice is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Author_Not_Connected') )

        # None --> Send Message.

        if Interaction.guild.voice_client is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Interaction.user.voice.channel.id is Interaction.guild.voice_client.channel.id

            if isAuthor:

                if Self.Queue.is_empty:

                    return await Interaction.response.send_message( await Self.getLocale(Interaction, 'Queue_Empty') )
                
                else:

                    await Self.VoiceBot.stop()

                    Self.IsSkiped = True

                    Interaction.response.is_done()

    async def onListButton(Self, Interaction : Interaction):

        # Author Not Connected
        
        if Interaction.user.voice is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Author_Not_Connected') )

        # None --> Send Message.

        if Interaction.guild.voice_client is None:

            return await Interaction.response.send_message( content = await Self.getLocale(Interaction, 'Im_Not_Connected') )

        # But If Is Already In Channel.

        else:

            isAuthor = Interaction.user.voice.channel.id is Interaction.guild.voice_client.channel.id

            if isAuthor:

                getQueue = Self.Queue.get_queue()

                Final = []

                for Track in range(len(getQueue)):

                    Final.append(getQueue[Track].title)

                return await Interaction.response.send_message(content = Final)

async def setup(Bot):

    await Bot.add_cog( MusicPlayer_Extension(Bot) )
